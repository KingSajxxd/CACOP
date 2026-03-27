# 🚧 Cost-Aware Chaos & Optimization Platform (CACOP)

Resilience is easy when money doesn't matter. Resilience that doesn't quietly drain your cloud budget is the real challenge.

CACOP is a local, cloud-native platform designed to intentionally inject failures into a Kubernetes environment, observe system behavior, and quantify the real financial cost of resilience—such as autoscaling spikes, retry storms, and wasted compute.

The goal isn't just uptime. It's building systems that are reliable and economically sane. To keep costs at exactly $0, this entire platform runs locally, simulating a cloud provider environment.

## 🏗️ Tech Stack

- **Infrastructure:** Local Kubernetes via Minikube (simulating AWS/GCP)
- **Target "Victim" Services:** Python (FastAPI)
- **Chaos Engine:** Chaos Mesh (Declarative fault injection)
- **Observability:** PLG Stack (Prometheus, Loki, Grafana)
- **FinOps Control Plane:** Python (FastAPI) to calculate financial waste based on K8s resource requests/limits
- **Frontend Dashboard:** React

## 🚀 Project Roadmap

- [x] **Phase 1: Foundation** - Build the "victim" Python microservice, containerize it, and deploy it to Minikube with strict resource requests/limits.
- [ ] **Phase 2: Observability** - Deploy the PLG stack and instrument the microservice to track CPU/Memory spikes.
- [ ] **Phase 3: Chaos** - Install Chaos Mesh and run automated failure experiments.
- [ ] **Phase 4: Cost Intelligence** - Build the FinOps backend to translate resource spikes into simulated dollar amounts.
- [ ] **Phase 5: Visualization** - Build the React dashboard to visualize cost vs. resilience trade-offs.

---

## 💻 Getting Started (Phase 1)

### Prerequisites

Ensure you have the following installed on your local machine:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [OrbStack](https://orbstack.dev/) (Ensure the daemon has at least 8GB+ of memory allocated)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### 1. Start the Cluster

Spin up the local Kubernetes cluster with enough resources to handle the full stack.
```bash
minikube start --cpus=4 --memory=8192
```

### 2. Point Docker to Minikube

Configure your terminal to use Minikube's internal Docker daemon. This allows Kubernetes to find the images we build locally without pushing to Docker Hub.
```bash
eval $(minikube docker-env)
```

### 3. Build the Victim Service

Build the FastAPI container image directly inside the Minikube environment.
```bash
docker build -t cacop-victim:v1 .
```

### 4. Deploy to Kubernetes

Apply the deployment and service manifests to spin up the pods.
```bash
kubectl apply -f k8s/deployment.yaml
```

### 5. Verify the Deployment

Check that the pods are running and the service is available.
```bash
kubectl get pods
kubectl get svc
```
