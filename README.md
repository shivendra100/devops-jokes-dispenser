## DevOps Joke Dispenser Application: A Project Journey
This document outlines the development and CI/CD setup for a simple joke-displaying application, detailing the steps I took using Azure DevOps, Docker, and Kubernetes (Minikube).

## 1. Local Development Setup
To get started, I first ensured my local environment had the necessary tools.

Prerequisites I ensured I had installed:
Python 3.x
Node.js and npm (or yarn)
Docker Desktop (with Kubernetes enabled) or Minikube
kubectl
An Azure DevOps Account
Building the Backend (Flask)
I created the backend service using Flask to serve random jokes:

I navigated to the backend/ directory: cd backend
I installed the Python dependencies: pip install -r requirements.txt
For local testing, I ran the application: python app.py (It ran on http://localhost:5000)
Building the Frontend (React)
Next, I developed the React frontend application to consume and display jokes from the backend:

I navigated to the frontend/ directory: cd frontend
I installed the Node.js dependencies: npm install
For local testing, I ran the application: npm start (It ran on http://localhost:3000)
I made sure my backend was running for data fetching during local development.
Setting up Local Kubernetes (Minikube)
To simulate a production environment locally, I decided to deploy to a Kubernetes cluster using Minikube:

I started my Minikube cluster: minikube start
I enabled the Ingress addon, which is crucial for external access: minikube addons enable ingress
I retrieved my Minikube IP address: minikube ip
I updated my system's hosts file by adding an entry like [MINIKUBE_IP] jokeapp.local (replacing [MINIKUBE_IP] with the actual IP).
On Windows, this file is at C:\Windows\System32\drivers\etc\hosts
On Linux/macOS, it's at /etc/hosts
For initial local testing, I manually applied the Kubernetes manifests:
Bash

kubectl apply -f kubernetes/
Note: I kept in mind that the CI/CD pipeline would handle this deployment automatically later.
2. Azure DevOps CI/CD Setup
With the local code ready, I then moved to setting up the Continuous Integration and Continuous Deployment pipelines in Azure DevOps.

2.1 Azure DevOps Account & Project
First, I ensured my Azure DevOps environment was ready:

I created an organization (e.g., yourname-devops-org) and a new project (e.g., DevOpsJokeApp) at dev.azure.com.
2.2 Azure Repos
I decided to use separate repositories for my backend and frontend code for better modularity:

I created two separate Git repositories in Azure Repos: backend and frontend.
I then pushed my respective codebases to these repositories from my local machine:
git remote add origin https://<ORG>@dev.azure.com/<ORG>/<PROJECT>/_git/backend
git push -u origin --all (I performed this for both my backend and frontend repos)
Branch Policies: To maintain code quality, I configured the master (or main) branch of both repositories:
I required a minimum of 1 reviewer for pull requests.
I enabled checking for linked work items (optional, but good practice).
I planned to enable build validation once my build pipelines were created.
2.3 Self-Hosted Agent
To allow Azure DevOps pipelines to interact with my local Minikube cluster, I configured my laptop as a self-hosted build agent:

I navigated to Organization settings -> Agent pools -> Default (or created a new pool).
I followed the instructions to download, install, and configure a new agent on my local Windows machine.
I generated a Personal Access Token (PAT) with "Agent Pools (Read & manage)", "Build (Read & execute)", and "Code (Read & write)" scopes, which I used during the agent configuration process.
2.4 Build Pipelines (YAML)
I created two separate build pipelines, one for each service, under Pipelines -> Pipelines. I ensured the pool name in each pipeline matched my self-hosted agent pool (which was Default).

Backend Build Pipeline (backend/.azure-pipelines-build.yml):
This pipeline is responsible for installing Python dependencies, preparing the Flask application, and packaging it along with the Kubernetes manifests into an artifact.

YAML

# (Full YAML content for Backend Build Pipeline as provided in the instructions)
trigger:
- master # Or 'main', depending on your default branch name

pool:
  name: Default # Or the name of your self-hosted agent pool

variables:
  python_version: '3.9'
  backend_folder: 'backend' # Assuming your backend code is in a 'backend' folder at repo root
  backend_artifact_name: 'backend-dist'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '$(python_version)'
    addToPath: true

- script: |
    pip install --upgrade pip
    pip install -r $(backend_folder)/requirements.txt
  displayName: 'Install Backend Dependencies'

# Package the backend code (e.g., zip it for deployment)
- script: |
    # Copy backend code to artifact staging directory
    mkdir $(Build.ArtifactStagingDirectory)/$(backend_folder)
    cp -r $(backend_folder)/* $(Build.ArtifactStagingDirectory)/$(backend_folder)/
    cp $(backend_folder)/.flaskenv $(Build.ArtifactStagingDirectory)/$(backend_folder)/ 2>$null || : # Copy .flaskenv if exists (ignore error if not)

    # Copy Kubernetes manifests from the root 'kubernetes' folder
    mkdir $(Build.ArtifactStagingDirectory)/kubernetes
    cp -r $(Build.SourcesDirectory)/kubernetes/* $(Build.ArtifactStagingDirectory)/kubernetes/
  displayName: 'Prepare Backend Artifact & Copy K8s Manifests'

- publish: $(Build.ArtifactStagingDirectory) # Publish the entire staging directory
  artifact: $(backend_artifact_name)
  displayName: 'Publish Backend Artifact'
Frontend Build Pipeline (frontend/.azure-pipelines-build.yml):
This pipeline builds the React application, installs Node.js dependencies, and packages the static files along with the Kubernetes manifests.

YAML

# (Full YAML content for Frontend Build Pipeline as provided in the instructions)
trigger:
- master # Or 'main', depending on your default branch name

pool:
  name: Default # Or the name of your self-hosted agent pool

variables:
  node_version: '18.x' # Or a specific Node.js version you prefer, e.g., '20.x'
  frontend_folder: 'frontend' # Assuming your frontend code is in a 'frontend' folder at repo root
  frontend_artifact_name: 'frontend-dist'

steps:
- task: NodeTool@0
  inputs:
    versionSpec: '$(node_version)'
  displayName: 'Install Node.js'

- script: |
    npm install
  workingDirectory: $(frontend_folder)
  displayName: 'Install Frontend Dependencies'

- script: |
    npm run build
  workingDirectory: $(frontend_folder)
  displayName: 'Build Frontend Application'

# Prepare Frontend Artifact and Copy Kubernetes Manifests
- script: |
    # Copy React build output
    cp -r $(frontend_folder)/build $(Build.ArtifactStagingDirectory)/$(frontend_folder)/build

    # Copy Kubernetes manifests from the root 'kubernetes' folder
    mkdir $(Build.ArtifactStagingDirectory)/kubernetes
    cp -r $(Build.SourcesDirectory)/kubernetes/* $(Build.ArtifactStagingDirectory)/kubernetes/
  displayName: 'Prepare Frontend Artifact & Copy K8s Manifests'

- publish: $(Build.ArtifactStagingDirectory) # Publish the entire staging directory
  artifact: $(frontend_artifact_name)
  displayName: 'Publish Frontend Artifact'
2.5 Release Pipelines
Finally, I created two release pipelines under Pipelines -> Releases to deploy my services to the local Minikube cluster.

Backend Release Pipeline:
This pipeline takes the backend build artifact, builds the Docker image, and applies the Kubernetes manifests for the backend service.

Artifacts: I linked the backend build pipeline and enabled the continuous deployment trigger.
Stage: I named the stage Deploy to Minikube.
Agent Job: I configured it to use my Default agent pool.
Tasks:
Docker Task (Build Image): I configured this to build the backend-joke-app:latest Docker image using the Dockerfile located within the _backend_build artifact.
Kubernetes Task (Apply Manifests): I set up a Kubernetes service connection using a Service Account (with my Minikube IP and a service account token obtained via kubectl). This task applies the backend-deployment.yaml and backend-service.yaml manifests.
Frontend Release Pipeline:
This pipeline handles the deployment of the frontend, building its Docker image, and applying its Kubernetes manifests, including the Ingress.

Artifacts: I linked the frontend build pipeline and enabled the continuous deployment trigger.
Stage: I named the stage Deploy to Minikube.
Agent Job: I configured it to use my Default agent pool.
Tasks:
Docker Task (Build Image): I configured this to build the frontend-joke-app:latest Docker image using the Dockerfile located within the _frontend_build artifact.
Kubernetes Task (Apply Manifests): I reused the existing Kubernetes service connection. This task applies the frontend-deployment.yaml, frontend-service.yaml, and minikube-ingress.yaml manifests.
3. Usage After CI/CD Deployment
After successfully configuring and running both release pipelines, my application was deployed to Minikube:

I ensured Minikube was running (minikube status).
I then opened my browser and navigated to http://jokeapp.local (or directly http://[YOUR_MINIKUBE_IP]).
The application was accessible, and I could verify that refreshing the page or clicking the button fetched new jokes from the backend running inside my Kubernetes cluster.

4. Troubleshooting During the Project
Throughout the setup, I kept the following troubleshooting tips in mind:

Agent not connecting: I checked PAT validity/scopes, server URL, and firewall settings.
Build failures: I reviewed pipeline logs for dependency issues, syntax errors, or incorrect paths.
Release failures: I examined Docker build logs and Kubernetes task logs for connection issues or manifest errors.
Application not accessible after deployment:
I confirmed Minikube was running (minikube status).
I checked Kubernetes deployment status: kubectl get deployments, kubectl get pods.
I verified service status: kubectl get services.
I checked ingress: kubectl get ingress.
I re-verified my hosts file entry for jokeapp.local.
I ensured imagePullPolicy: Never meant images were built on the same machine as the Minikube cluster (which they were with the self-hosted agent).
I ensured the frontend API URL (http://jokeapp.local/api/joke) correctly pointed to my Minikube Ingress.
