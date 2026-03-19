#!/usr/bin/env python3

import requests
import json
import time

# n8n webhook (replace with your own)
WEBHOOK_URL = "http://<YOUR_N8N_SERVER>/webhook/wazuh-alert"

# Wazuh alerts file
LOG_FILE = "/var/ossec/logs/alerts/alerts.json"

with open(LOG_FILE, "r") as f:
    # Move to end of file (read only new alerts)
    f.seek(0, 2)

    while True:
        line = f.readline()

        if not line:
            time.sleep(1)
            continue

        try:
            alert = json.loads(line)

            # Extract Windows event data (if present)
            eventdata = alert.get("data", {}).get("win", {}).get("eventdata", {})

            # Try multiple possible IP fields
            srcip = (
                eventdata.get("ipAddress") or
                eventdata.get("IpAddress") or
                eventdata.get("sourceIp") or
                alert.get("srcip") or
                alert.get("agent", {}).get("ip") or
                "unknown"
            )

            data = {
                "rule": alert.get("rule", {}).get("description", "unknown"),
                "level": alert.get("rule", {}).get("level", 0),
                "srcip": srcip,
                "agent": alert.get("agent", {}).get("name", "unknown")
            }

            # Send alert to n8n
            response = requests.post(WEBHOOK_URL, json=data)

            print("Alert sent:", data)
            print("Response code:", response.status_code)

        except json.JSONDecodeError:
            # Skip incomplete log lines
            continue

        except Exception as e:
            print("Error:", e)