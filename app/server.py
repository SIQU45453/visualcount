"""VisualCount V1 server.

Runs the shelf-product detector on your own computer. Open the page from your
phone on the same Wi-Fi to take a photo, draw an area and count products.
"""
import io
import os
import socket
from datetime import datetime

import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from PIL import Image, ImageOps
from pydantic import BaseModel
from transformers import AutoImageProcessor, AutoModelForObjectDetection

MODEL_ID = os.environ.get("VC_MODEL", "is36e/detr-resnet-50-sku110k")
THRESHOLD = float(os.environ.get("VC_THRESHOLD", "0.5"))
HERE = os.path.dirname(os.path.abspath(__file__))

torch.set_num_threads(max(1, (os.cpu_count() or 2)))
print(f"Loading model {MODEL_ID} (first start downloads about 170 MB)...")
processor = AutoImageProcessor.from_pretrained(MODEL_ID)
model = AutoModelForObjectDetection.from_pretrained(MODEL_ID).eval()
print("Model ready.")

app = FastAPI(title="VisualCount")


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def clean_boxes(boxes, scores):
    """Remove duplicates: overlapping boxes (NMS) and small boxes sitting
    inside a bigger one (e.g. a bottle cap inside a bottle)."""
    order = np.argsort(-scores)
    kept = []
    for i in order:
        if all(iou(boxes[i], boxes[j]) < 0.5 for j in kept):
            kept.append(i)
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    final = []
    for i in kept:
        bi = boxes[i]
        nested = False
        for j in kept:
            bj = boxes[j]
            if i == j or area(bj) <= area(bi):
                continue
            ix = max(0.0, min(bi[2], bj[2]) - max(bi[0], bj[0]))
            iy = max(0.0, min(bi[3], bj[3]) - max(bi[1], bj[1]))
            if ix * iy > 0.6 * area(bi):
                nested = True
                break
        if not nested:
            final.append(i)
    return final


@app.post("/api/detect")
async def detect(image: UploadFile = File(...)):
    try:
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(await image.read()))).convert("RGB")
    except Exception:
        raise HTTPException(400, "That file is not a photo the app can read. Try a JPG or PNG.")
    im.thumbnail((1600, 1600))
    w, h = im.size
    with torch.no_grad():
        out = model(**processor(images=im, return_tensors="pt"))
    res = processor.post_process_object_detection(out, threshold=THRESHOLD, target_sizes=[(h, w)])[0]
    boxes = res["boxes"].numpy()
    scores = res["scores"].numpy()
    keep = clean_boxes(boxes, scores)
    items = [
        {
            "x0": round(float(boxes[i][0]) / w, 4), "y0": round(float(boxes[i][1]) / h, 4),
            "x1": round(float(boxes[i][2]) / w, 4), "y1": round(float(boxes[i][3]) / h, 4),
            "score": round(float(scores[i]), 3),
        }
        for i in keep
    ]
    return {"width": w, "height": h, "boxes": items}


class Row(BaseModel):
    time: str
    product: str
    count: int
    ai_count: int
    added: int
    removed: int
    photo: str = ""


class ExportBody(BaseModel):
    rows: list[Row]


@app.post("/api/export")
def export(body: ExportBody):
    wb = Workbook()
    ws = wb.active
    ws.title = "Counts"
    ws.append(["Time", "Product / area", "Final count", "AI count", "Added by hand", "Removed by hand", "Photo"])
    for r in body.rows:
        ws.append([r.time, r.product, r.count, r.ai_count, r.added, r.removed, r.photo])
    for col, width in zip("ABCDEFG", (20, 28, 12, 10, 14, 16, 24)):
        ws.column_dimensions[col].width = width
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    name = f"visualcount-{datetime.now():%Y%m%d-%H%M}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@app.get("/")
def index():
    return FileResponse(os.path.join(HERE, "static", "index.html"))


app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("VC_PORT", "8000"))
    print("\n  On this computer:  http://localhost:%d" % port)
    print("  On your phone:     http://%s:%d   (same Wi-Fi)\n" % (lan_ip(), port))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
