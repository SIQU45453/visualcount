import sys, glob, os, json, time, csv
from PIL import Image, ImageOps
import torch, supervision as sv, numpy as np
torch.set_num_threads(4)
model_name=sys.argv[1]; out=f"results/{model_name}"; os.makedirs(out,exist_ok=True)
photos=sorted(glob.glob('photos/*.jpg'))
skip={'img25.jpg','img37.jpg'}
photos=[p for p in photos if os.path.basename(p) not in skip]
if model_name.startswith('rfdetr'):
    from rfdetr import RFDETRSmall, RFDETRNano
    m=(RFDETRSmall if 'small' in model_name else RFDETRNano)()
    def detect(im):
        d=m.predict(im,threshold=0.3); return d
elif model_name in ('detr_sku','dfine_sku'):
    from transformers import AutoImageProcessor, AutoModelForObjectDetection
    mid={'detr_sku':'is36e/detr-resnet-50-sku110k','dfine_sku':'benjamintli/dfine-xl_sku110k'}[model_name]
    proc=AutoImageProcessor.from_pretrained(mid); m=AutoModelForObjectDetection.from_pretrained(mid).eval()
    def detect(im):
        with torch.no_grad():
            inp=proc(images=im,return_tensors='pt'); o=m(**inp)
            r=proc.post_process_object_detection(o,threshold=float(os.environ.get('TH','0.4')),target_sizes=[im.size[::-1]])[0]
        d=sv.Detections(xyxy=r['boxes'].numpy().reshape(-1,4),confidence=r['scores'].numpy(),class_id=np.zeros(len(r['scores']),int))
        return d.with_nms(threshold=0.5,class_agnostic=True)
else:
    from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
    mid={'gdino':'IDEA-Research/grounding-dino-tiny','owlv2':'google/owlv2-base-patch16-ensemble'}[model_name]
    proc=AutoProcessor.from_pretrained(mid); m=AutoModelForZeroShotObjectDetection.from_pretrained(mid).eval()
    labels=["product","bottle","box","bag","package","can","jar"]
    def detect(im):
        with torch.no_grad():
            if model_name=='gdino':
                inp=proc(images=im,text=[labels],return_tensors='pt'); o=m(**inp)
                r=proc.post_process_grounded_object_detection(o,inp.input_ids,threshold=0.25,text_threshold=0.2,target_sizes=[im.size[::-1]])[0]
            else:
                inp=proc(images=im,text=[labels],return_tensors='pt'); o=m(**inp)
                # owlv2 pads to square; use max side as target
                s=max(im.size); r=proc.post_process_grounded_object_detection(o,threshold=0.2,target_sizes=torch.tensor([[s,s]]))[0]
        b=r['boxes'].numpy(); sc=r['scores'].numpy()
        d=sv.Detections(xyxy=b.reshape(-1,4),confidence=sc,class_id=np.zeros(len(sc),int))
        # drop boxes covering >25% of image (whole-shelf boxes)
        area=(d.xyxy[:,2]-d.xyxy[:,0])*(d.xyxy[:,3]-d.xyxy[:,1]); d=d[area<0.25*im.size[0]*im.size[1]]
        return d.with_nms(threshold=0.5,class_agnostic=True)
rows=[]
for p in photos:
    im=ImageOps.exif_transpose(Image.open(p)).convert('RGB'); t=time.time(); d=detect(im); dt=time.time()-t
    n=len(d); rows.append({'photo':os.path.basename(p)[:-4],'count':n,'seconds':round(dt,2)})
    a=sv.BoxAnnotator(thickness=3).annotate(np.array(im).copy(),d); Image.fromarray(a).save(f"{out}/{os.path.basename(p)}",quality=80)
    print(model_name,os.path.basename(p),n,round(dt,1),flush=True)
with open(f"{out}/counts.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=['photo','count','seconds']); w.writeheader(); w.writerows(rows)
