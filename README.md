# incident-bot

A webhook receiver that listens for Grafana alerts, assigns severity levels, logs them as structured incidents, and posts colour-coded notifications to Slack.

Built to work alongside [sre-observability](https://github.com/britishchip/sre-observability). When a Grafana alert fires, it hits this bot instead of a generic webhook.

```
Grafana alert --> /webhook --> severity classification --> Slack #incidents
                                      |
                                 /incidents (audit log)
```

## How it works

Grafana sends a POST request to `/webhook` when an alert fires. The bot reads the alert payload, assigns a severity level based on the alert name, generates a unique incident ID, and posts a colour-coded message to a Slack channel. Every incident is also stored in memory and accessible via `/incidents`.

Severity is determined by keywords in the alert name:

| Level | Colour | Trigger |
|-------|--------|---------|
| P1 | Red | Alert name contains "critical" |
| P2 | Orange | Alert name contains "error" or "slo" |
| P3 | Green | Everything else |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Receives Grafana alert payloads |
| `/incidents` | GET | Returns all logged incidents as JSON |
| `/health` | GET | Health check |

## Running locally

Copy the example env file and add your Slack webhook URL:

```bash
cp .env.example .env
```

Install dependencies and start the bot:

```bash
pip install -r requirements.txt
python bot.py
```

The bot runs on port 6000. Test it with a sample alert payload:

```bash
curl -X POST http://localhost:6000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [
      {
        "status": "firing",
        "labels": {
          "alertname": "SLO Breach - Success Rate"
        },
        "annotations": {
          "summary": "Success rate dropped below 99%"
        }
      }
    ]
  }'
```

Check the incident was logged:

```bash
curl http://localhost:6000/incidents
```

You should see a message in your Slack channel and a JSON response with the incident ID, timestamp, and severity.

## Deploy to Kubernetes

Assumes k3s is running and the bot image has been imported into containerd.

Build and import the image:

```bash
sudo docker build -t incident-bot:latest .
sudo docker save incident-bot:latest | sudo k3s ctr images import -
```

Deploy:

```bash
sudo KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl apply -f deployment.yaml
```

Get the cluster IP:

```bash
sudo KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl get svc incident-bot -n monitoring
```

Point Grafana to it:

1. Go to Alerting > Contact points > Add contact point
2. Type: Webhook
3. URL: `http://<CLUSTER-IP>:6000/webhook`
4. Go to Alerting > Notification policies and set it as the default contact point

## Environment variables

| Variable | Description |
|----------|-------------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL from api.slack.com |

## Project structure

```
incident-bot/
  bot.py            Flask app, webhook handler, incident logger
  requirements.txt
  Dockerfile
  deployment.yaml   Kubernetes Deployment and Service
  .env.example      Environment variable template
```
