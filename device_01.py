# device_01.py
# Simulates device-01 connecting to AWS IoT Core
# This device has an INTENTIONALLY BAD (overly permissive) policy
# Device Defender will flag this during the audit

from awsiot import mqtt_connection_builder
from awscrt import mqtt
import time
import json

# ── CONFIG ──────────────────────────────────────────────────────────────────
ENDPOINT    = "a1w57eer55jydf-ats.iot.ap-south-1.amazonaws.com"
CLIENT_ID   = "device-01"
TOPIC       = "iot/device-01/telemetry"

CERT_PATH   = r"C:\iot-mini-project\certs\device-01\certificate.pem.crt"
KEY_PATH    = r"C:\iot-mini-project\certs\device-01\private.pem.key"
CA_PATH     = r"C:\iot-mini-project\certs\device-01\AmazonRootCA1.pem"
# ────────────────────────────────────────────────────────────────────────────


def on_connection_interrupted(connection, error, **kwargs):
    print(f"[device-01] Connection interrupted: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"[device-01] Connection resumed. Return code: {return_code}")


def main():
    print("[device-01] Building MQTT connection...")

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

    print("[device-01] Connecting to AWS IoT Core...")
    connect_future = mqtt_connection.connect()
    connect_future.result()  # blocks until connected
    print("[device-01] ✅ Connected successfully!")
    print("[device-01] NOTE: This device has an OVERLY PERMISSIVE policy (iot:* on *)")
    print("[device-01] Device Defender will flag this in the next audit.\n")

    # Publish simulated telemetry data every 5 seconds
    message_count = 0
    try:
        while True:
            message_count += 1
            payload = {
                "device_id": "device-01",
                "temperature": 28.5 + message_count * 0.1,
                "humidity": 65.0,
                "status": "active",
                "message_number": message_count,
                "misconfiguration": "overly_permissive_policy"
            }
            mqtt_connection.publish(
                topic=TOPIC,
                payload=json.dumps(payload),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            print(f"[device-01] Published message #{message_count} to {TOPIC}")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n[device-01] Stopping...")

    finally:
        print("[device-01] Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("[device-01] Disconnected.")


if __name__ == "__main__":
    main()
