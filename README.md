# Diamond Price Prediction & Evaluation Portal

A production-grade, multi-process cloud architecture deploying an end-to-end Machine Learning inference workspace. This repository unifies a high-performance **FastAPI Backend REST API** (which serves a scikit-learn diamond valuation pipeline) with an interactive **Streamlit Frontend Consumer UI Portal**. 

The entire runtime environment is consolidated into a single, optimized **Docker Container Architecture** overseen by **Supervisor Process Management** and architected for continuous deployment to an **AWS EKS (Elastic Kubernetes Service)** cluster via an automated **GitHub Actions CI/CD Pipeline**.

---

## 🗺️ Architectural Ecosystem Overview

The deployment pattern transitions from a local engineering environment to a high-availability, self-healing cloud cluster following this systemic data flow:
[ Local Workstation ]│ (Git Push to main branch)▼[ GitHub Repository ] ────► Triggers ────► [ GitHub Actions CI/CD Runner ]│├── 1. Codebase Checkout & Lint├── 2. Auth via AWS IAM Secrets├── 3. Build Single Unified Docker Image└── 4. Push Image Tag to Amazon ECR│▼[ Amazon EKS Cluster ](Rollout Restart Pod Deployment)│┌─────────────────┴─────────────────┐▼                                   ▼[ Pod Instance Node 1 ]             [ Pod Instance Node 2 ]┌─────────────────────┐             ┌─────────────────────┐│  [ Supervisor Engine]             │  [ Supervisor Engine]│   ├── FastAPI (:8000)             │   ├── FastAPI (:8000)│   └── Streamlit (:8501)           │   └── Streamlit (:8501)└──────────┬──────────┘             └──────────┬──────────┘│                                   │└─────────────────┬─────────────────┘▲│ (Routes Traffic via Port 80)[ AWS Network Load Balancer ]▲│ (HTTPS Client Access)[ End User / UI ]
1. **Version Control Ledger:** Programmatic code modifications and operational manifests are committed to GitHub. Large raw datasets (`.zip`) and binary model weights (`.pkl`) are decoupled from Git version tracking using optimized rules within the `.gitignore` ledger to prevent repository bloating.
2. **Automated Integration Pipeline:** GitHub Actions instantiates an ephemeral Linux environment, validates credentials using cryptographically secured repository secrets (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`), containerizes the code via a multi-process Docker blueprint, and publishes the immutable target artifact into **Amazon Elastic Container Registry (ECR)**.
3. **Orchestration & Routing Grid:** **Amazon EKS** orchestrates a rolling updates matrix across multi-AZ compute instances (`t3.medium` Node Groups). A managed Kubernetes Service provisions an external **AWS Elastic Load Balancer (ELB)**, mapping public port `80` to the containerized Streamlit Portal interface on port `8501`.
4. **Internal Micro-networking Loop:** Within each executing Kubernetes Pod, the Streamlit frontend UI routes internal pipeline requests over the local loopback adapter directly to the FastAPI layer (`http://127.0.0.1:8000/predict`), establishing an ultra-low-latency process communication mesh.

---

## 📂 Project Directory Structure

```text
Diamond_Price_prediction/                  # Root Application Workspace Context
│
├── .github/
│   └── workflows/
│       └── deploy.yml                     # GitHub Actions CI/CD Declarative Pipeline
│
├── artifacts/
│   └── diamond_pipeline.pkl               # Serialized scikit-learn ML Pipeline (Excluded from Git)
│
├── backend/
│   ├── main.py                            # FastAPI Application Server & ML Inference Logic
│   └── pipeline.py                        # Analytical Training, Pipeline Blueprint & Utilities
│
├── data/                                  # Local Data Staging Directory (Excluded from Git)
│   └── archive (20).zip                   # Raw Compressed Diamond Features Dataset
│
├── frontend/
│   └── app.py                             # Streamlit Interactive Consumer Web Portal
│
├── k8s/
│   └── deployment.yaml                    # Kubernetes Unified Deployment & LoadBalancer Service Manifest
│
├── .gitignore                             # Version Control Exclusion Target System Rules
├── docker-compose.yml                     # Local Multi-Process Container Orchestration Blueprint
├── Dockerfile                             # Production Multi-Stage, Process-Managed Container Core
├── requirements.txt                       # Consolidated Application Dependency Ledger
└── supervisord.conf                       # Process Monitor and Daemon Manager Control Configuration
🛠️ Unified Dependency Configuration (requirements.txt)The environment utilizes a singular, pinned dependency management architecture. This eliminates compilation discrepancies between your local virtual machine (venv) and the runtime container instances.Plaintext# --- Core Web & Server ---
fastapi==0.136.3
uvicorn==0.49.0
pydantic==2.13.4
pydantic_core==2.46.4
python-multipart==0.0.32

# --- Machine Learning & Data Processing ---
scikit-learn==1.6.1
joblib==1.5.3
pandas==3.0.3
numpy==2.4.6
scipy==1.17.1

# --- Frontend Portal Interface ---
streamlit==1.58.0
requests==2.34.2
🐳 Containerization & Process SupervisionThe Production Process ChallengeStandard Docker execution patterns enforce a strict one-process-per-container constraint. Invoking multiple long-lived background daemons using a shell sequencing operator (e.g., uvicorn ... & streamlit ...) risks creating zombie processes. If the machine learning backend crashes due to memory allocation bounds, the outer container remains active because the frontend is alive, serving broken pages to clients.The Supervisor Architecture SolutionOur workflow integrates Supervisor (supervisord) inside a unified Debian-slim base runtime image. Supervisor acts as an explicit internal init process manager (PID 1) that spawns, monitors, and traps standard outputs for both microservices.Process Configuration (supervisord.conf)Ini, TOML[supervisord]
nodaemon=true
user=root
logfile=/dev/stdout
logfile_maxbytes=0

[program:backend_api]
command=uvicorn backend.main:app --host 0.0.0.0 --port 8000
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
autorestart=true
startretries=3

[program:frontend_ui]
command=python -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
autorestart=true
startretries=3
Production Dockerfile Framework (Dockerfile)DockerfileFROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/artifacts/diamond_pipeline.pkl

WORKDIR /app

# Install compilation system requirements and Process Manager
RUN apt-get update && apt-get install -y --no-install-recommends gcc supervisor && rm -rf /var/lib/apt/lists/*

# Layer Cache Dependency Mechanism
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Bind Code and Assets Contexts
COPY ./backend ./backend
COPY ./frontend ./frontend
COPY ./artifacts ./artifacts
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
EXPOSE 8501

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
💻 Local Workspace Engineering Guide1. Traditional Execution EnvironmentTo execute components bare-metal on your workstation for debugging purposes:Bash# Initialize and source local virtual environment
source venv/Scripts/activate

# Validate dependency presence 
pip install -r requirements.txt

# Launch FastAPI Sub-Engine independently
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# In a separate terminal session, launch Frontend Portal
streamlit run frontend/app.py --server.port 8501
2. Standardized Local Container TestingTo guarantee complete functional parity with the cloud deployment model, execute the integrated services locally via Docker Compose:Bash# Build the unified image layers and initiate the multi-process supervisor locally
docker compose up --build
Client Frontend Portal URL: http://localhost:8501Swagger API Documentation Sandbox: http://localhost:8000/docsHealth Validation Probe: http://localhost:8000/health🚀 Cloud Infrastructure Deployment SequenceFollow these operational steps to execute a complete bare-metal infrastructure rollout on AWS.Step 1: Secure Source Control StorageBecause your serialized ML model (diamond_pipeline.pkl) totals 327.08 MB, it violates GitHub's absolute object push constraint of 100.00 MB. To bypass tracking blockades, clear old commit cache frames and establish clean tracking configurations:Bash# Purge compromised local cache history
rm -rf .git
git init
git branch -M main

# Stage environment profiles and codebase elements
git add .
git commit -m "feat: unified web setup omitting massive binaries"

# Rebind remote source link and push code layers
git remote add origin [https://github.com/vijaymangore/Diamond-price-prediction-aws-deployment.git](https://github.com/vijaymangore/Diamond-price-prediction-aws-deployment.git)
git push -u origin main
(Note: Upload your physical model binary diamond_pipeline.pkl directly to your production cloud server storage path or target deployment engine mount during initial runtime startup).Step 2: Provision Cloud Container Registries (Amazon ECR)Navigate to the AWS Management Console $\rightarrow$ Amazon Elastic Container Registry (ECR).Select Create Private Repository.Define the programmatic namespace identifier: diamond-unified-app.Extract the generated repository URI string (Format: YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/diamond-unified-app).Step 3: Establish the Managed Elastic Kubernetes Service (Amazon EKS)Navigate to Amazon EKS $\rightarrow$ Create Cluster.Assign the cluster naming index: diamond-production-cluster. Maintain default subnetwork routing definitions.Once the cluster lifecycle transitions to an Active operational state, navigate to the Compute sub-tab $\rightarrow$ Add Node Group.Configure compute resources: Name the group diamond-workers, select instance configuration layout size t3.medium, and establish a scaling threshold value of 2 desired runtime instances across zones.Step 4: Configure GitHub Pipeline Secret KeysTo grant GitHub Actions cryptographic rights to access AWS, map your access identity credentials inside your GitHub repository settings panel:Navigate to your online GitHub codebase $\rightarrow$ Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions.Create AWS_ACCESS_KEY_ID: Input your AWS programmatic user access string.Create AWS_SECRET_ACCESS_KEY: Input your secure private IAM credential token value.Step 5: Update Manifest Target Environs & Execute BuildOpen k8s/deployment.yaml on your workstation.Update the container image string configuration element on line 18 with your real, validated 12-digit AWS ECR registry namespace URI location:YAMLimage: [123456789012.dkr.ecr.us-east-1.amazonaws.com/diamond-unified-app:latest](https://123456789012.dkr.ecr.us-east-1.amazonaws.com/diamond-unified-app:latest)
Commit and push the structural configuration changes to your main branch:Bashgit add k8s/deployment.yaml
git commit -m "deploy: bind authentic cloud container tracking uri"
git push origin main
📈 Kubernetes Infrastructure Orchestration (k8s/deployment.yaml)This declarative manifest automates a rolling rollout strategy across your AWS EKS cluster nodes, provisioning an internet-accessible Network Load Balancer directed straight to your user application interface.YAMLapiVersion: apps/v1
kind: Deployment
metadata:
  name: diamond-unified-deployment
  labels:
    app: diamond-app
spec:
  replicas: 2 # Scale redundant pods across multi-availability zone node hardware
  selector:
    matchLabels:
      app: diamond-app
  template:
    metadata:
      labels:
        app: diamond-app
    spec:
      containers:
      - name: unified-container
        image: YOUR_AWS_ACCOUNT_[ID.dkr.ecr.us-east-1.amazonaws.com/diamond-unified-app:latest](https://ID.dkr.ecr.us-east-1.amazonaws.com/diamond-unified-app:latest)
        ports:
        - containerPort: 8501 # Streamlit Public Application Portal Web Port
        - containerPort: 8000 # FastAPI Internal Core ML Engine Port
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: diamond-unified-service
spec:
  type: LoadBalancer # Instructs AWS to dynamically provision a physical hardware edge load balancer
  ports:
  - port: 80         # Public standard browser HTTP portal entry point
    targetPort: 8501 # Forwards traffic straight into the containerized Streamlit application UI layer
  selector:
    app: diamond-app
⚙️ Automated CI/CD Pipeline Automation (.github/workflows/deploy.yml)YAMLname: Production Single-Dockerfile CI/CD Pipeline

on:
  push:
    branches: [ "main" ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Source Code Checkout
      uses: actions/checkout@v4

    - name: Configure AWS Credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Authenticate AWS Container Registry (ECR)
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build, Tag, and Push Single Unified Image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
      run: |
        docker build -t $ECR_REGISTRY/diamond-unified-app:latest .
        docker push $ECR_REGISTRY/diamond-unified-app:latest

    - name: Connect to AWS EKS Cluster
      run: aws eks update-kubeconfig --region us-east-1 --name diamond-production-cluster

    - name: Deploy Unified App to Kubernetes Cluster
      run: |
        kubectl apply -f k8s/deployment.yaml
        kubectl rollout restart deployment/diamond-unified-deployment
🔒 Security Signature Verification ModelThe Backend API implements an explicit structural header authentication layer to block illicit external programmatic crawling vectors. All API execution calls must include a client API token within the transaction payload context.Header Validation BlueprintAuthentication Header Key Required: X-API-KeyValid Production Token Signatures: Vijay@10, prod-secret-diamond-key-9988Sample Inference Execution Request (cURL)Bashcurl -X 'POST' \
  'http://<YOUR-AWS-LOADBALANCER-URL>/predict' \
  -H 'accept: application/json' \
  -H 'X-API-Key: Vijay@10' \
  -H 'Content-Type: application/json' \
  -d '{
  "carat": 0.23,
  "cut": "Ideal",
  "color": "E",
  "clarity": "SI2",
  "depth": 61.5,
  "table": 55.0,
  "x": 3.95,
  "y": 3.98,
  "z": 2.43
}'
Developed and containerized by Vijay Mangore for high-availability cloud serving paradigms.
### 🚀 To Push Your Documentation to GitHub:
Now that your repository push is working cleanly without the large files blocker, add this file and push it up so it formats nicely on your repository home page:

```bash
git add README.md
git commit -m "docs: add comprehensive architectural readme overview"
git push origin main