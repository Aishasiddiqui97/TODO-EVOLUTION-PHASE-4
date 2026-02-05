@echo off
REM Deployment script for Event-Driven Todo Chatbot - Phase V MVP
REM Deploys to local Kubernetes (Minikube) on Windows

echo.
echo 🚀 Event-Driven Todo Chatbot - Phase V Deployment
echo ==================================================
echo.

REM Check prerequisites
echo 📋 Checking prerequisites...

where kubectl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ kubectl not found. Please install kubectl.
    exit /b 1
)

where minikube >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ minikube not found. Please install minikube.
    exit /b 1
)

where dapr >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ dapr CLI not found. Please install Dapr CLI.
    exit /b 1
)

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ docker not found. Please install Docker.
    exit /b 1
)

echo ✅ All prerequisites found
echo.

REM Start Minikube if not running
echo 🔧 Starting Minikube...
minikube status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    minikube start --cpus=4 --memory=8192
) else (
    echo ✅ Minikube already running
)
echo.

REM Initialize Dapr
echo 🔧 Initializing Dapr on Kubernetes...
kubectl get namespace dapr-system >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    dapr init -k
) else (
    echo ✅ Dapr already initialized
)
echo.

REM Create secrets
echo 🔐 Creating secrets...
set /p OPENAI_API_KEY="Enter your OpenAI API key: "
kubectl create secret generic app-secrets --from-literal=openai-api-key="%OPENAI_API_KEY%" --dry-run=client -o yaml | kubectl apply -f -
echo ✅ Secrets created
echo.

REM Deploy infrastructure
echo 📦 Deploying infrastructure...
kubectl apply -f k8s/local/postgres.yaml
kubectl apply -f k8s/local/redpanda.yaml
echo ✅ Infrastructure deployed
echo.

REM Wait for infrastructure
echo ⏳ Waiting for infrastructure to be ready...
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
echo ✅ Infrastructure ready
echo.

REM Deploy Dapr components
echo 🔧 Deploying Dapr components...
kubectl apply -f k8s/dapr/
echo ✅ Dapr components deployed
echo.

REM Build and load Chat API image
echo 🏗️  Building Chat API image...
docker build -t chat-api:latest -f backend/Dockerfile .
echo ✅ Image built
echo.

echo 📤 Loading image into Minikube...
minikube image load chat-api:latest
echo ✅ Image loaded
echo.

REM Deploy Chat API
echo 🚀 Deploying Chat API...
kubectl apply -f k8s/services/chat-api-deployment.yaml
kubectl apply -f k8s/services/chat-api-service.yaml
echo ✅ Chat API deployed
echo.

REM Wait for Chat API
echo ⏳ Waiting for Chat API to be ready...
kubectl wait --for=condition=ready pod -l app=chat-api --timeout=180s
echo ✅ Chat API ready
echo.

REM Display status
echo 📊 Deployment Status
echo ====================
kubectl get pods
echo.

REM Port forwarding instructions
echo 🌐 Access Instructions
echo ======================
echo.
echo To access the Chat API, run:
echo   kubectl port-forward svc/chat-api 8000:8000
echo.
echo Then visit:
echo   http://localhost:8000
echo.
echo API Documentation:
echo   http://localhost:8000/docs
echo.
echo Health Check:
echo   curl http://localhost:8000/health
echo.
echo ✅ Deployment complete!
pause
