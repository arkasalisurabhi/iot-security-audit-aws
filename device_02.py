# device_02.py
# Simulates device-02 connecting to AWS IoT Core
# This device represents a scenario where IoT logging is DISABLED
# Device Defender will flag the logging_disabled misconfiguration

from awsiot import mqtt_connection_builder
from awscrt import mqtt
import time
import json

# ── CONFIG ──────────────────────────────────────────────────────────────────
ENDPOINT    = "a1w57eer55jydf-ats.iot.ap-south-1.amazonaws.com"
CLIENT_ID   = "device-02"
TOPIC       = "iot/device-02/telemetry"

CERT_PATH   = r"C:\iot-mini-project\certs\device-02\certificate.pem.crt"
KEY_PATH    = r"C:\iot-mini-project\certs\device-02\private.pem.key"
CA_PATH     = r"C:\iot-mini-project\certs\device-02\AmazonRootCA1.pem"
# ────────────────────────────────────────────────────────────────────────────


def on_connection_interrupted(connection, error, **kwargs):
    print(f"[device-02] Connection interrupted: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"[device-02] Connection resumed. Return code: {return_code}")


def main():
    print("[device-02] Building MQTT connection...")

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

    print("[device-02] Connecting to AWS IoT Core...")
    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("[device-02] ✅ Connected successfully!")
    print("[device-02] NOTE: IoT logging is DISABLED for this device's account-level config")
    print("[device-02] Device Defender will flag LOGGING_DISABLED in the next audit.\n")

    message_count = 0
    try:
        while True:
            message_count += 1
            payload = {
                "device_id": "device-02",
                "temperature": 31.0 + message_count * 0.05,
                "humidity": 70.0,
                "status": "active",
                "message_number": message_count,
                "misconfiguration": "logging_disabled"
            }
            mqtt_connection.publish(
                topic=TOPIC,
                payload=json.dumps(payload),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            print(f"[device-02] Published message #{message_count} to {TOPIC}")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n[device-02] Stopping...")

    finally:
        print("[device-02] Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("[device-02] Disconnected.")


if __name__ == "__main__":
    main()
