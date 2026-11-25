# VisualCount V1

Count products in a shelf photo from your phone. The AI runs on your own computer;
your phone just opens a web page on the same Wi-Fi. No photo leaves your network.

## One-time setup (about 10 minutes)

1. Install **Python 3.11 or newer** from https://www.python.org/downloads/
   - Windows: on the first installer screen, tick **"Add python.exe to PATH"**.
2. Copy this `app` folder to your computer (for example to your Desktop).

## Start it

- **Windows:** double-click `start-windows.bat`
- **Mac:** double-click `start-mac.command`
  (if macOS blocks it: right-click > Open > Open)

The first start installs the libraries and downloads the AI model (about 170 MB),
so it takes a few minutes. Later starts take about 15 seconds.

When it is ready, the window shows two addresses:

```
On this computer:  http://localhost:8000
On your phone:     http://192.168.1.23:8000   (same Wi-Fi)
```

Type the phone address into your phone's browser. Keep the window open while you use the app.
If the phone can't connect, allow Python through your computer's firewall when asked.

## Using it

1. **Take or choose photo.** The computer counts every product it sees (about 1-3 seconds).
2. **Draw area.** Drag your finger over the shelf section you want. Only products inside count.
3. **Fix boxes.** Tap a wrong box to remove it (red X). Tap a missed product to add it (orange dot).
4. Type a name (for example "Oil 5L") and tap **Save count**.
5. **Export Excel** downloads all saved counts.

## Known limits

- Works best on shelves of boxes, packs and small bottles.
- Big bottles and jugs are often counted twice (the cap and the body get separate boxes).
  Remove the extras in step 3.
- Model: `is36e/detr-resnet-50-sku110k` (Apache-2.0 weights, trained on the SKU-110K shelf dataset).
  Check the SKU-110K dataset licence before any commercial use.
