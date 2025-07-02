"""
Stream‑picker + ROI selector for RTSP cameras
--------------------------------------------

1.  Scans the IP list and tries the usual vendor‑specific RTSP paths.
2.  Lets you pick a working camera.
3.  Shows the live stream.
4.  Grabs the very first good frame from that same stream so you can
    draw a rectangle (ROI) with the mouse.
5.  Prints the rectangle’s coordinates when you press “q”.
"""

import cv2
import socket
import time

# ---------- camera credentials & discovery -------------
USERNAME  = "admin"
PASSWORD  = "admin@567"
PORT      = 554
TIMEOUT   = 1          # seconds to wait for a TCP handshake

IP_LIST = [
    "192.168.1.38",
]

# Common RTSP path patterns for Dahua, Hikvision, ONVIF…
RTSP_PATHS = [
    "/cam/realmonitor?channel=1&subtype=0",
    "/Streaming/Channels/101",
    "/h264",                           # many generic / ONVIF
]

def is_rtsp_port_open(ip: str, port: int = PORT, timeout: int = TIMEOUT) -> bool:
    """Quick TCP handshake check—fast way to skip offline hosts."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def first_working_rtsp(ip: str) -> str | None:
    """
    Try each vendor path until cv2.VideoCapture can actually read a frame.
    Return the first working rtsp:// URL—or None.
    """
    for path in RTSP_PATHS:
        url = f"rtsp://{USERNAME}:{PASSWORD}@{ip}:{PORT}{path}"
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            # read one frame to prove it really works
            ok, _ = cap.read()
            cap.release()
            if ok:
                return url
    return None


# ---------- network scan ----------
working_streams: list[str] = []

print("🔍 Scanning for active RTSP cameras...\n")
for ip in IP_LIST:
    print(f"• Checking {ip} … ", end="", flush=True)
    if not is_rtsp_port_open(ip):
        print("🚫 port closed")
        continue

    stream = first_working_rtsp(ip)
    if stream:
        print("✅ FOUND")
        working_streams.append(stream)
    else:
        print("❌ no stream")

if not working_streams:
    print("\n❌ No working cameras discovered — exiting.")
    quit()

# ---------- user picks a camera ----------
print("\n📸 Available cameras:")
for idx, url in enumerate(working_streams, start=1):
    print(f"  {idx}. {url}")

try:
    cam_idx = int(input("Enter the number of the camera to view: ")) - 1
    SELECTED_URL = working_streams[cam_idx]
except (ValueError, IndexError):
    print("❌ Invalid selection.")
    quit()

# ---------- open the chosen stream ----------
print(f"\n[*] Opening live stream:\n    {SELECTED_URL}")
cap = cv2.VideoCapture(SELECTED_URL, cv2.CAP_FFMPEG)
if not cap.isOpened():
    print("❌ Failed to open the stream.")
    quit()

print("[*] Waiting for the first good frame …")
while True:
    ret, frame = cap.read()
    if ret:
        break
    time.sleep(0.05)

# ------------------------------------------------------------------
#  ROI / rectangle drawing section
# ------------------------------------------------------------------
drawing = False
ix = iy = -1             # initial rectangle corner
rect_coords = (0, 0, 0, 0)
frame_disp = frame.copy()

def mouse_cb(event, x, y, flags, _param):
    global drawing, ix, iy, rect_coords, frame_disp

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        frame_disp = frame.copy()

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        frame_disp = frame.copy()
        cv2.rectangle(frame_disp, (ix, iy), (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect_coords = (ix, iy, x, y)
        cv2.rectangle(frame_disp, (ix, iy), (x, y), (0, 255, 0), 2)

cv2.namedWindow("Draw ROI (press 'q' to save)")
cv2.setMouseCallback("Draw ROI (press 'q' to save)", mouse_cb)

while True:
    cv2.imshow("Live view (press 'ESC' to quit)", frame)
    cv2.imshow("Draw ROI (press 'q' to save)", frame_disp)
    if cv2.waitKey(1) & 0xFF in (27,):  # ESC kills everything
        rect_coords = None
        break
    if cv2.waitKey(1) & 0xFF in (ord('q'),):
        break
    # keep reading new frames for live view
    ok, frame = cap.read()
    if not ok:
        print("[-] Lost connection.")
        break

cap.release()
cv2.destroyAllWindows()

# ---------- results ----------
if rect_coords:
    x1, y1, x2, y2 = rect_coords
    print(f"\n🎯 Rectangle selected:  x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    print([x1, y1, x2, y2])
else:
    print("\nNo rectangle selected.")
