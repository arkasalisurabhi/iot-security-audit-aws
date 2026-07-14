import boto3
import json
import os

# Initialize AWS clients
iot_client = boto3.client('iot', region_name='ap-south-1')
sns_client = boto3.client('sns', region_name='ap-south-1')

# Your SNS topic ARN — paste yours here
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:XXXXXXXXXXXX:iot-security-alerts"

# Minimal safe policy to replace bad ones with
SAFE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:Connect",
                "iot:Publish",
                "iot:Subscribe",
                "iot:Receive"
            ],
            "Resource": "arn:aws:iot:ap-south-1:*:client/${iot:ClientId}"
        }
    ]
}


def lambda_handler(event, context):
    print("Event received:", json.dumps(event))
    
    try:
        # Parse the finding from Security Hub via EventBridge
        detail = event.get('detail', {})
        findings = detail.get('findings', [])
        
        if not findings:
            print("No findings in event")
            return {"status": "no findings"}
        
        for finding in findings:
            finding_type = finding.get('Title', '')
            severity = finding.get('Severity', {}).get('Label', 'UNKNOWN')
            description = finding.get('Description', '')
            resources = finding.get('Resources', [])
            
            print(f"Processing finding: {finding_type} | Severity: {severity}")
            
            # Handle overly permissive policy
            if 'POLICY_OVERLY_PERMISSIVE' in finding_type or 'overly permissive' in finding_type.lower():
                remediated = remediate_overly_permissive_policies()
                send_alert(
                    finding_type=finding_type,
                    severity=severity,
                    description=description,
                    action_taken=f"Auto-remediated {remediated} overly permissive policies"
                )
            
            # Handle logging disabled
            elif 'LOGGING_DISABLED' in finding_type or 'logging' in finding_type.lower():
                enable_iot_logging()
                send_alert(
                    finding_type=finding_type,
                    severity=severity,
                    description=description,
                    action_taken="Auto-enabled IoT logging"
                )
            
            # Any other finding — just alert, don't auto-fix
            else:
                send_alert(
                    finding_type=finding_type,
                    severity=severity,
                    description=description,
                    action_taken="Alert sent — manual review required"
                )
        
        return {"status": "success", "findings_processed": len(findings)}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e


def remediate_overly_permissive_policies():
    """Find all overly permissive IoT policies and replace with safe version"""
    remediated_count = 0
    
    try:
        # List all IoT policies
        response = iot_client.list_policies()
        policies = response.get('policies', [])
        
        for policy in policies:
            policy_name = policy['policyName']
            
            # Skip the clean device-03 policy
            if 'clean' in policy_name.lower():
                continue
            
            # Get current policy document
            policy_response = iot_client.get_policy(policyName=policy_name)
            policy_doc = json.loads(policy_response['policyDocument'])
            
            # Check if overly permissive (iot:* or Resource: *)
            for statement in policy_doc.get('Statement', []):
                actions = statement.get('Action', [])
                resource = statement.get('Resource', '')
                
                if isinstance(actions, str):
                    actions = [actions]
                
                is_permissive = (
                    'iot:*' in actions or
                    resource == '*' or
                    resource == 'arn:aws:iot:*:*:*'
                )
                
                if is_permissive:
                    print(f"Remediating policy: {policy_name}")
                    
                    # Create new policy version with safe document
                    iot_client.create_policy_version(
                        policyName=policy_name,
                        policyDocument=json.dumps(SAFE_POLICY),
                        setAsDefault=True
                    )
                    remediated_count += 1
                    print(f"Policy {policy_name} remediated successfully")
                    break
    
    except Exception as e:
        print(f"Error remediating policies: {str(e)}")
    
    return remediated_count


def enable_iot_logging():
    """Enable IoT logging at account level"""
    try:
        # Get or create an IAM role for IoT logging
        iam_client = boto3.client('iam', region_name='ap-south-1')
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        iot_client.set_v2_logging_options(
            roleArn=f"arn:aws:iam::{account_id}:role/iot-auto-audit-role_1782315423071",
            defaultLogLevel='WARN',
            disableAllLogs=False
        )
        print("IoT logging enabled successfully")
    
    except Exception as e:
        print(f"Error enabling logging: {str(e)}")


def send_alert(finding_type, severity, description, action_taken):
    """Send SNS email alert"""
    message = f"""
🚨 AWS IoT Security Alert 🚨

Finding Type : {finding_type}
Severity     : {severity}
Description  : {description}

Action Taken : {action_taken}

--
AWS IoT Security Audit Framework
Mini Project — Automated IoT Security Configuration Audit
"""
    
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"[{severity}] IoT Security Finding: {finding_type}",
            Message=message
        )
        print(f"SNS alert sent for: {finding_type}")
    
    except Exception as e:
        print(f"Error sending SNS alert: {str(e)}")