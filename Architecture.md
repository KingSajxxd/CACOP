Your Linux Server (HP)
│
├── Minikube (Kubernetes cluster)
│   │
│   ├── Namespace: default
│   │   └── victim-service pod (FastAPI, port 8000)
│   │       ├── /health   → Kubernetes checks this every 10s
│   │       ├── /api/normal → normal traffic simulation
│   │       └── /api/stress → CPU spike trigger
│   │
│   └── Namespace: monitoring (being set up now)
│       ├── Prometheus     → collects metrics every 15s
│       ├── Grafana        → draws the graphs
│       ├── AlertManager   → sends alerts
│       ├── node-exporter  → host CPU/RAM metrics
│       └── kube-state-metrics → K8s object state
│
└── GitHub Actions Runner (actions-runner/)
    └── Listens for git pushes → auto builds + deploys