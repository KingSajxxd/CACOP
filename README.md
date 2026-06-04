# 🚧 Cost-Aware Chaos & Optimization Platform (CACOP)

Resilience is easy when money doesn't matter. Resilience that doesn't quietly drain your cloud budget is the real challenge.

CACOP is a self-hosted, cloud-native platform that intentionally injects failures into a Kubernetes environment, observes system behavior, and quantifies the **real financial cost** of resilience — autoscaling spikes, retry storms, and wasted compute.

The goal isn't just uptime. It's building systems that are reliable **and** economically sane. This entire platform runs on a local Linux server at exactly **$0**, simulating a cloud provider environment.

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Infrastructure** | Kubernetes via Minikube on a self-hosted Linux server |
| **Victim Service** | Python (FastAPI) — intentionally stressable microservice |
| **CI/CD** | GitHub Actions with a local self-hosted runner |
| **Chaos Engine** | Chaos Mesh — declarative fault injection |
| **Metrics** | Prometheus — time-series scraping every 15s |
| **Visualization** | Grafana — live dashboards with cost thresholds |
| **FinOps Engine** | Python (FastAPI) — translates CPU/RAM spikes into simulated AWS costs |
| **Frontend** | React — cost vs. resilience dashboard |
| **Remote Access** | Tailscale mesh VPN |

---

## 🚀 Project Roadmap

- [x] **Phase 1: Foundation** — Python victim microservice containerized with Docker and deployed to Kubernetes with strict CPU/memory resource limits
- [x] **Phase 1.5: CI/CD** — GitHub Actions pipeline with local self-hosted runner; every `git push` automatically builds and deploys to the cluster
- [x] **Phase 2: Observability** — kube-prometheus-stack deployed; custom CACOP FinOps Engine dashboard built in Grafana with live CPU, memory, and simulated dollar cost panels
- [ ] **Phase 3: Chaos** — Install Chaos Mesh and run declarative failure experiments (CPU hog, pod kill, network latency)
- [ ] **Phase 4: Cost Intelligence** — FastAPI control plane queries Prometheus and calculates the exact financial cost of each chaos experiment
- [ ] **Phase 5: Visualization** — React dashboard displaying cost vs. resilience trade-offs in real time

---

## 📊 Proven Results (Phase 2)

| State | Simulated AWS Cost/hr | Multiplier |
|---|---|---|
| Idle (normal operation) | $0.000079 | baseline |
| `/api/stress` triggered | $0.011704 | **148x more expensive** |

One unoptimized API call makes the infrastructure **148x more expensive per hour**. CACOP measures and visualizes this in real time.

---

## 💻 Getting Started

### Prerequisites

- Linux server (or VM) with at least 4 CPUs and 8GB RAM
- [Docker](https://docs.docker.com/engine/install/ubuntu/) installed and running
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- (Optional) [Tailscale](https://tailscale.com/) for remote browser access

---

### Phase 1: Victim Service

#### 1. Start the cluster
```bash
minikube start --driver=docker --cpus=4 --memory=8192
```

#### 2. Point Docker at Minikube's internal registry
```bash
eval $(minikube docker-env)
```

#### 3. Build the victim service image
```bash
docker build -t cacop-victim:latest .
```

#### 4. Deploy to Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods
```

#### 5. Test the endpoints
```bash
# Port-forward the service
kubectl port-forward svc/victim-service 8000:80

# Health check
curl http://localhost:8000/health

# Trigger a 30-second CPU stress test
curl -X POST "http://localhost:8000/api/stress?duration=30"
```

---

### Phase 1.5: CI/CD Pipeline

The GitHub Actions pipeline uses a **local self-hosted runner** — it runs on the same Linux server as the cluster, giving it direct access to Minikube.

**Setup:**
1. Go to your GitHub repo → Settings → Actions → Runners → New self-hosted runner
2. Select Linux and follow the install steps into an `actions-runner/` directory
3. Start the runner: `cd actions-runner && ./run.sh`

**What the pipeline does on every push to `master`:**
```
git push origin master
    → GitHub notifies the local runner
    → eval $(minikube docker-env)
    → docker build -t cacop-victim:latest .
    → kubectl apply -f k8s/deployment.yaml
    → kubectl rollout restart deployment victim-service
    → kubectl get pods
```

---

### Phase 2: Observability Stack

#### 1. Deploy Prometheus + Grafana via Helm
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring

helm install cacop-monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

#### 2. Make port-forwards permanent with systemd

Create a systemd service for each tool so they start automatically on boot and restart on failure:

```bash
# Grafana
sudo tee /etc/systemd/system/cacop-grafana.service << EOF
[Unit]
Description=CACOP - Grafana Port Forward
After=network.target

[Service]
User=$USER
Environment=KUBECONFIG=/home/$USER/.kube/config
ExecStart=/usr/local/bin/kubectl port-forward svc/cacop-monitoring-grafana -n monitoring --address 0.0.0.0 3000:80
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Prometheus
sudo tee /etc/systemd/system/cacop-prometheus.service << EOF
[Unit]
Description=CACOP - Prometheus Port Forward
After=network.target

[Service]
User=$USER
Environment=KUBECONFIG=/home/$USER/.kube/config
ExecStart=/usr/local/bin/kubectl port-forward svc/cacop-monitoring-kube-prom-prometheus -n monitoring --address 0.0.0.0 9090:9090
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Victim Service
sudo tee /etc/systemd/system/cacop-victim.service << EOF
[Unit]
Description=CACOP - Victim Service Port Forward
After=network.target

[Service]
User=$USER
Environment=KUBECONFIG=/home/$USER/.kube/config
ExecStart=/usr/local/bin/kubectl port-forward svc/victim-service --address 0.0.0.0 8000:80
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now cacop-grafana cacop-prometheus cacop-victim
```

#### 3. Access the dashboards

| Tool | URL | Credentials |
|---|---|---|
| Grafana | `http://<server-ip>:3000` | admin / (see below) |
| Prometheus | `http://<server-ip>:9090` | none |
| Victim API | `http://<server-ip>:8000` | none |

Get the Grafana admin password:
```bash
kubectl get secret --namespace monitoring cacop-monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

#### 4. PromQL queries used in the CACOP dashboard

```promql
# CPU cores currently used
sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"victim-service-.*", cpu="total"}[1m]))

# Memory in use
sum(container_memory_working_set_bytes{namespace="default", pod=~"victim-service-.*"})

# Simulated AWS cost ($/hr) — based on ~$0.048 per vCPU-hour
sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"victim-service-.*", cpu="total"}[1m])) * 0.048
```

> **Note for Minikube with containerd:** The `container` label is not attached to cAdvisor metrics. Use `pod=~"victim-service-.*"` instead of `container="victim-api"`. In Grafana, set the Stat panel **Color scheme** to `From thresholds (by value)` — the default `Classic palette` overrides threshold colors.

---

## 📁 Project Structure

```
cacop-victim/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml          # GitHub Actions pipeline
├── k8s/
│   └── deployment.yaml         # Kubernetes Deployment + Service
├── actions-runner/             # GitHub self-hosted runner (not committed)
├── main.py                     # FastAPI victim service
├── Dockerfile                  # Production-grade container image
├── requirements.txt
└── README.md
```

---

## 🔑 Key Concepts

| Concept | What it means in CACOP |
|---|---|
| **Resource Requests** | CPU/RAM reserved for the pod — what cloud providers bill you for |
| **Resource Limits** | Hard cap on usage — hitting this is where cost spikes happen |
| **PromQL `rate()`** | Converts raw CPU counter into "cores currently being used" |
| **Chaos Experiment** | A declarative YAML file describing a failure to inject |
| **Simulated Cost** | `CPU cores used × $0.048/hr` — mirrors real AWS on-demand pricing |

---

## 🛑 Important

- Never run `minikube delete` — this destroys the Prometheus/Grafana installation
- Always start Docker before running `minikube start`
- The GitHub Actions runner (`actions-runner/`) is excluded from git via `.gitignore`
