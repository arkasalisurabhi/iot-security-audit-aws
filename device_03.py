# device_03.py
# Simulates device-03 connecting to AWS IoT Core
# This device has a NORMAL, correctly scoped policy
# Used as a baseline/control device - Device Defender should NOT flag this one

from awsiot import mqtt_connection_builder
from awscrt import mqtt
import time
import json

# ── CONFIG ──────────────────────────────────────────────────────────────────
ENDPOINT    = "a1w57eer55jydf-ats.iot.ap-south-1.amazonaws.com"
CLIENT_ID   = "device-03"
TOPIC       = "iot/device-03/telemetry"

CERT_PATH   = r"C:\iot-mini-project\certs\device-03\certificate.pem.crt"
KEY_PATH    = r"C:\iot-mini-project\certs\device-03\private.pem.key"
CA_PATH     = r"C:\iot-mini-project\certs\device-03\AmazonRootCA1.pem"
# ────────────────────────────────────────────────────────────────────────────


def on_connection_interrupted(connection, error, **kwargs):
    print(f"[device-03] Connection interrupted: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"[device-03] Connection resumed. Return code: {return_code}")


def main():
    print("[device-03] Building MQTT connection...")

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_id=CLIENT_ID,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        clean_session=False,
        keep_alive_secs=30
    )

    print("[device-03] Connecting to AWS IoT Core...")
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("[device-03] ✅ Connected successfully!")
    print("[device-03] This is a CLEAN device with correct policy scoping.")
    print("[device-03] Device Defender should NOT flag this device.\n")

    message_count = 0
    try:
        while True:
            message_count += 1
            payload = {
                "device_id": "device-03",
                "temperature": 25.0,
                "humidity": 60.0,
                "status": "active",
                "message_number": message_count,
                "misconfiguration": "none"
            }
            mqtt_connection.publish(
                topic=TOPIC,
                payload=json.dumps(payload),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            print(f"[device-03] Published message #{message_count} to {TOPIC}")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n[device-03] Stopping...")

    finally:
        print("[device-03] Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("[device-03] Disconnected.")


if __name__ == "__main__":
    main()
