"""
iot/esp32_client.py
Placeholder integration point for real ESP32 sensor nodes and the relay/pump
controller. Today the dashboard runs on services/simulator.py; once hardware
is on the network, implement the functions below (REST polling or an MQTT
subscriber) and swap the call site in routes/api.py from the simulator to
this module. Keeping the interface identical means no other code changes.
"""


def fetch_latest_reading(device_id: str):
    """
    TODO: Replace with an HTTP GET to the ESP32's REST endpoint, e.g.:
        resp = requests.get(f"http://{device_ip}/api/reading", timeout=3)
        return resp.json()
    or subscribe to an MQTT topic such as `selamet/{device_id}/sensors`.
    """
    raise NotImplementedError("Connect real ESP32 hardware here.")


def send_relay_command(device_id: str, turn_on: bool, duration_seconds: int = 30):
    """
    TODO: Replace with an HTTP POST / MQTT publish to trigger the misting
    relay on the target ESP32, e.g.:
        requests.post(f"http://{device_ip}/api/relay", json={...})
    """
    raise NotImplementedError("Connect real ESP32 relay control here.")
