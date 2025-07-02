"""
Draw a bounding box on the first frame of a video source, save it to coords.json,
and reuse it the next time you run the script.

• Choose source: RTSP link / video file / webcam (Enter)
• If coords.json is present, optionally reuse the saved rectangle
• Press and drag left mouse button to draw; press q to confirm
"""

from pathlib import Path
import json
import cv2
import sys

# ── 0. Load previously saved rectangle if it exists ────────────────────────────
coords_file = Path("coords.json")
loaded_coords = None           # will become a list like [x1, y1, x2, y2]

if coords_file.exists():
    try:
        loaded_coords = json.loads(coords_file.read_text())
        if len(loaded_coords) != 4:
            loaded_coords = None
    except Exception:
        loaded_coords = None   # corrupted file → ignore

# ── 1. Pick the video source ───────────────────────────────────────────────────
source = input(
    "Paste an RTSP link, type a video‑file path (e.g. output.mp4), "
    "or press <Enter> for the webcam:\n>>> "
).strip()
if source == "":
    source = 0  # default camera
# (OpenCV handles RTSP URLs and file paths automatically)

# ── 2. Grab the first frame ────────────────────────────────────────────────────
cap = cv2.VideoCapture(source)
ret, frame = cap.read()
cap.release()

if not ret:
    sys.exit("❌  Couldn’t read from the chosen source. Check the URL/path or camera.")

# ── 3. Use saved rectangle or draw a new one? ──────────────────────────────────
if loaded_coords:
    reuse = input(
        f"Found saved rectangle {loaded_coords}. "
        "Press <Enter> to reuse it, or type n to draw a new one: "
    ).lower() != "n"
else:
    reuse = False

if reuse:
    x1, y1, x2, y2 = loaded_coords
    print("Using saved rectangle:", loaded_coords)

else:
    # --- Set up globals for the mouse callback ---
    drawing, ix, iy = False, -1, -1
    rect_coords = [0, 0, 0, 0]
    frame_copy = frame.copy()

    def draw_rectangle(event, x, y, flags, param):
        global drawing, ix, iy, rect_coords, frame_copy, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing, ix, iy = True, x, y
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            frame_copy[:] = frame       # reset to original
            cv2.rectangle(frame_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            rect_coords = [ix, iy, x, y]
            cv2.rectangle(frame_copy, (ix, iy), (x, y), (0, 255, 0), 2)

    # --- Interactive drawing window ---
    cv2.namedWindow("Draw Rectangle")
    cv2.setMouseCallback("Draw Rectangle", draw_rectangle)

    while True:
        cv2.imshow("Draw Rectangle", frame_copy)
        if cv2.waitKey(1) & 0xFF == ord("q"):   # press q to confirm
            break

    cv2.destroyAllWindows()

    x1, y1, x2, y2 = rect_coords
    loaded_coords = rect_coords   # keep for later code

    # ── 4. Save the rectangle for next time ────────────────────────────────────
    coords_file.write_text(json.dumps(rect_coords))
    print(f"Saved rectangle {rect_coords} to {coords_file.resolve()}")

# ── 5. Rectangle ready to use in variable `loaded_coords` ──────────────────────
print("Final rectangle coordinates:", loaded_coords)

# -------------------------------------------------------------------
# From here on, continue with your own processing logic, e.g.:
#   • crop = frame[y1:y2, x1:x2]
#   • tracking, detection, etc.
# -------------------------------------------------------------------
