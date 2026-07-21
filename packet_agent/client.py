import requests
from config import API_URL, DEVICE_NAME, REQUEST_TIMEOUT


def get_capture_status():
    try:
        response = requests.get(
            f"{API_URL}/agent/status/{DEVICE_NAME}",
            timeout=REQUEST_TIMEOUT
        )

        data = response.json()

        print(data)

        return data.get("capture", False)

    except Exception as e:
        print("Status Error:", e)
        return False


def send_packet(packet):

    try:
        requests.post(
            f"{API_URL}/ingest",
            json=packet,
            timeout=REQUEST_TIMEOUT
        )

    except Exception as e:
        print("Send Error:", e)

def heartbeat():

    try:

        response = requests.post(
            f"{API_URL}/agent/heartbeat",
            json={
                "device": DEVICE_NAME
            },
            timeout=REQUEST_TIMEOUT
        )

        print(response.status_code)
        print(response.text)

    except Exception as e:

        print("Heartbeat Error:", e)