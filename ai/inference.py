"""
ai/inference.py
Placeholder for future computer-vision inference on hive camera frames.
Intended pipeline once wired up:
    frame -> YOLOv8n / YOLOv11n (bee + hive-entrance detection)
          -> tracker (bee counting, foraging vs resting classification)
          -> TensorFlow Lite health/heat-stress/absconding models
The Live Camera page currently reads simulated results from
models.camera_info.CameraDetection (see services/simulator or the /api
camera-analysis endpoint). Swap the data source here without touching
the frontend once a real model is trained and exported.
"""


def detect_bees(frame_bytes: bytes):
    """
    TODO: Load a YOLOv8n/YOLOv11n TFLite model and run inference on `frame_bytes`.
    Return a dict like:
        {"bee_count": int, "flying": int, "resting": int, "boxes": [...]}
    """
    raise NotImplementedError("Wire up YOLOv8n/YOLOv11n + TensorFlow Lite here.")


def classify_colony_health(sensor_features: dict):
    """
    TODO: Replace with a trained model (health score, heat stress,
    absconding probability) once labeled field data is available.
    Until then, services/prediction_service.py's rule engine is used.
    """
    raise NotImplementedError("Train and load a real colony-health model here.")
