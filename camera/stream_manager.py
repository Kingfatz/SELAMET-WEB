"""
camera/stream_manager.py
Placeholder for real ESP32-CAM / IP-camera / RTSP stream handling.
For MJPEG/HTTP cameras the <img> tag in templates/camera.html can often
point straight at the camera's stream URL. For RTSP, this module is where
you'd bridge to an MJPEG proxy (e.g. via ffmpeg or a library such as
`aiortc`/`opencv-python`) since browsers cannot play RTSP natively.
"""


def get_stream_url(camera_info) -> str:
    """Return a browser-playable URL for the given CameraInfo row."""
    if camera_info.stream_type in ("mjpeg", "http"):
        return camera_info.stream_url
    # RTSP needs transcoding/proxying before a browser can render it.
    raise NotImplementedError("Add an RTSP-to-MJPEG/HLS bridge for this stream type.")


def check_camera_online(camera_info) -> bool:
    """
    TODO: Replace with a real reachability check, e.g. a short HTTP HEAD
    request to the camera or an MQTT heartbeat topic.
    """
    return camera_info.status == "online"
