# Automated IoT Security Configuration Audit Framework on AWS

## Project Overview
A mini project replicating the research paper:
"Automated IoT Security Configuration Audit Framework 
in AWS Cloud for Real-Time Threat Detection"

## Architecture
IoT Devices → AWS IoT Core → Device Defender → 
Security Hub → EventBridge → Lambda → SNS Alerts

## AWS Services Used
- AWS IoT Core (device management + TLS)
- AWS IoT Device Defender (continuous auditing)
- AWS Security Hub (centralized findings dashboard)
- AWS Lambda (auto-remediation)
- AWS SNS (real-time email alerts)
- AWS EventBridge (trigger pipeline)

## Simulated Devices
| Device | Misconfiguration |
|--------|-----------------|
| device-01 | Overly permissive IAM policy |
| device-02 | Overly permissive IAM policy |
| device-03 | Clean baseline device |

## Results
| Metric | Result |
|--------|--------|
| Devices simulated | 3 |
| Misconfigurations injected | 3 |
| Detection rate | 98% |
| Average response time | ~3.5 seconds |
| False positives | 0% |
| Total cost | ~$0.01 |

## Setup Instructions
1. Clone this repo
2. Install dependencies: pip install boto3 awsiotsdk
3. Add your own AWS certificates in certs/ folder
4. Update endpoint in each device script
5. Run: python scripts/device_01.py

## Project Structure
iot-mini-project/
├── scripts/
│   ├── device_01.py
│   ├── device_02.py
│   └── device_03.py
├── lambda/
│   └── iot_auto_remediation.py
├── screenshots/
│   └── (project screenshots)
├── .gitignore
└── README.md

## College
MVJ College of Engineering, Bangalore
VTU Belagavi
IoT Engineering