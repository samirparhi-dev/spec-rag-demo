#!/usr/bin/env python3

import schedule
import time
import requests
import yaml
from datetime import datetime

# Load config
with open('scheduled_prompts.yaml') as f:
    config = yaml.safe_load(f)

OPEN_WEBUI_URL = "http://localhost:3000"
GITLAB_API_URL = "https://gitlab.com/api/v4"

def run_prompt(schedule_config):
    """Execute a scheduled prompt in Open WebUI"""
    prompt = schedule_config['prompt']
    
    # Call Open WebUI API
    response = requests.post(
        f"{OPEN_WEBUI_URL}/api/chat/completions",
        json={
            "model": "llama3.1:8b",
            "messages": [
                {"role": "system", "content": "You are an MLSecOps assistant."},
                {"role": "user", "content": prompt}
            ],
            "rag_enabled": True,
            "collection": "mlsecops-specs"
        },
        headers={"Authorization": f"Bearer {OPEN_WEBUI_TOKEN}"}
    )
    
    result = response.json()
    answer = result['choices'][^3_0]['message']['content']
    
    # Check if alert threshold met
    if schedule_config.get('alert_threshold'):
        if should_alert(answer, schedule_config['alert_threshold']):
            send_notification(schedule_config, answer)
    
    return answer

def should_alert(answer, threshold):
    """Determine if response warrants an alert"""
    keywords = {
        'critical_cve': ['CRITICAL', 'HIGH severity', 'exploit available'],
        'high_drop_rate': ['high rate', 'unexpected DROP', 'misconfiguration'],
        'security_risk': ['overly permissive', 'security risk', 'should be restricted']
    }
    
    return any(keyword.lower() in answer.lower() for keyword in keywords.get(threshold, []))

def send_notification(schedule_config, answer):
    """Send alert via configured channels"""
    for channel in schedule_config.get('notification', []):
        if channel == 'gitlab_issue':
            create_gitlab_issue(schedule_config['name'], answer)
        elif channel == 'slack_webhook':
            send_slack_alert(schedule_config['name'], answer)

def create_gitlab_issue(title, description):
    """Create GitLab issue for alert"""
    requests.post(
        f"{GITLAB_API_URL}/projects/{PROJECT_ID}/issues",
        headers={"PRIVATE-TOKEN": GITLAB_TOKEN},
        json={
            "title": f"[MLSecOps Alert] {title}",
            "description": f"## Automated Analysis\n\n{description}",
            "labels": ["mlsecops", "auto-generated", "security"]
        }
    )

# Schedule all prompts
for sched in config['schedules']:
    if 'cron' in sched:
        schedule.every().hour.at(sched['cron'].split()[^3_1]).do(
            run_prompt, sched
        )

print("Scheduled prompt runner started")
while True:
    schedule.run_pending()
    time.sleep(60)