# DevOps Joke Dispenser

This project demonstrates a simple CI/CD pipeline for a joke-displaying application using Azure DevOps, Docker, and Kubernetes (Minikube).

## Local Development Setup

### Prerequisites

* Python 3.x
* Node.js and npm (or yarn)
* Docker Desktop (with Kubernetes enabled) or Minikube
* kubectl
* Azure DevOps Account

### Backend (Flask)

1.  Navigate to `backend/`: `cd backend`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the application: `python app.py` (Runs on `http://localhost:5000`)

### Frontend (React)

1.  Navigate to `frontend/`: `cd frontend`
2.  Install dependencies: `npm install`
3.  Run the application: `npm start` (Runs on `http://localhost:3000`)
    * Ensure backend is running for data fetching.
![image](https://github.com/user-attachments/assets/954b8ca2-8b20-46a2-9d3e-2b342623f10c)


### Local Kubernetes (Minikube)

1.  **Start Minikube:** `minikube start`
2.  **Enable Ingress:** `minikube addons enable ingress`
3.  **Get Minikube IP:** `minikube ip`
4.  **Update your hosts file:** Add an entry like `[MINIKUBE_IP] jokeapp.local` (replace `[MINIKUBE_IP]` with the actual IP from the previous step).
    * Windows: `C:\Windows\System32\drivers\etc\hosts`
    * Linux/macOS: `/etc/hosts`
5.  **Apply Kubernetes Manifests (Manual, for local testing):**
    ```bash
    kubectl apply -f kubernetes/
    ```
    *Note: The CI/CD pipeline will handle this automatically.*

## Azure DevOps CI/CD Setup

### 1. Azure DevOps Account & Project

* Create an organization shivendrasingh100 and a project [dev.azure.com](https://dev.azure.com/shivendrasingh100).

### 2. Azure Repos

* Create two separate Git repositories: `backend` and `frontend`.
* Push the respective codebases to these repositories.
    * `git remote add origin https://dev.azure.com/shivendrasingh100/_git/backend
    * `git push -u origin --all

### 3. Self-Hosted Agent

* Go to **Organization settings** -> **Agent pools** -> `Default` (or create a new pool).
* Add a new agent and follow the instructions to install and configure it on your local machine.
* Generate a **Personal Access Token (PAT)** with "Agent Pools (Read & manage)", "Build (Read & execute)", "Code (Read & write)" scopes, and use it during agent configuration.

### 4. Build Pipelines (YAML)

Create two build pipelines under **Pipelines** -> **Pipelines**.
Ensure the `pool` name matches your self-hosted agent pool (e.g., `Default`).

* **Backend Build Pipeline (`backend/.azure-pipelines-build.yml`):**
    ```yaml
    # (Content as provided in step 6.A above, including the step to copy kubernetes folder)
    ```
* **Frontend Build Pipeline (`frontend/.azure-pipelines-build.yml`):**
    ```yaml
    # (Content as provided in step 6.B above, including the step to copy kubernetes folder)
    ```

### 5. Release Pipelines

Create two release pipelines under **Pipelines** -> **Releases**.

* **Backend Release Pipeline:**
    * **Artifacts:** Link the `backend` build pipeline. Enable continuous deployment trigger.
    * **Stage:** `Deploy to Minikube`
    * **Agent Job:**
        * Agent pool: `Default`
        * Tasks:
            1.  **Docker Task (Build Image):**
                * Command: `build`
                * Image Name: `backend-joke-app:latest`
                * Dockerfile: `$(System.DefaultWorkingDirectory)/_backend_build/backend/Dockerfile`
                * Build context: `$(System.DefaultWorkingDirectory)/_backend_build/backend`
            2.  **Kubernetes Task (Apply Manifests):**
                * Service Connection: Create a new `Kubernetes service connection` using `Service Account`.
                    * Cluster URL: `https://<YOUR_MINIKUBE_IP>:8443`
                    * Service Account Token: Obtain from `kubectl get secret $(kubectl get serviceaccount default -o jsonpath='{.secrets[0].name}') -o jsonpath='{.data.token}' | base64 --decode`
                * Command: `apply`
                * Configuration files: `$(System.DefaultWorkingDirectory)/_backend_build/kubernetes/backend-deployment.yaml,$(System.DefaultWorkingDirectory)/_backend_build/kubernetes/backend-service.yaml`

* **Frontend Release Pipeline:**
    * **Artifacts:** Link the `frontend` build pipeline. Enable continuous deployment trigger.
    * **Stage:** `Deploy to Minikube`
    * **Agent Job:**
        * Agent pool: `Default`
        * Tasks:
            1.  **Docker Task (Build Image):**
                * Command: `build`
                * Image Name: `frontend-joke-app:latest`
                * Dockerfile: `$(System.DefaultWorkingDirectory)/_frontend_build/frontend/Dockerfile`
                * Build context: `$(System.DefaultWorkingDirectory)/_frontend_build/frontend`
            2.  **Kubernetes Task (Apply Manifests):**
                * Service Connection: Use the existing Kubernetes service connection.
                * Command: `apply`
                * Configuration files: `$(System.DefaultWorkingDirectory)/_frontend_build/kubernetes/frontend-deployment.yaml,$(System.DefaultWorkingDirectory)/_frontend_build/kubernetes/frontend-service.yaml,$(System.DefaultWorkingDirectory)/_frontend_build/kubernetes/minikube-ingress.yaml`

## Usage After CI/CD Deployment

Once both release pipelines successfully deploy:

1.  Ensure Minikube is running (`minikube status`).
2.  Open your browser and navigate to `http://jokeapp.local` (or `http://[YOUR_MINIKUBE_IP]`).

The application should be accessible, and refreshing the page or clicking the button should fetch new jokes from the backend running in Kubernetes.

## Troubleshooting

* **Agent not connecting:** Check PAT validity/scopes, server URL, and firewall.
* **Build failures:** Review pipeline logs for dependency issues, syntax errors, or incorrect paths.
* **Release failures:** Check Docker build logs, Kubernetes task logs for connection issues, or manifest errors.
* **Application not accessible:**
    * Verify Minikube is running (`minikube status`).
    * Check Kubernetes deployment status: `kubectl get deployments`, `kubectl get pods`.
    * Check service status: `kubectl get services`.
    * Check ingress: `kubectl get ingress`.
    * Verify your `hosts` file entry for `jokeapp.local`.
    * If using `imagePullPolicy: Never`, ensure the images are built on the same machine as the Minikube cluster (which they are if using a self-hosted agent on the same machine).
    * Ensure the backend API URL in `frontend/src/App.js` correctly points to your Minikube Ingress (e.g., `http://jokeapp.local/api/joke`).
