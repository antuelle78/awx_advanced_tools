#!/bin/bash

# AWX Advanced Tools Kubernetes Deployment Script
# This script deploys all components to Kubernetes with proper ordering

set -e

echo "🚀 Deploying AWX Advanced Tools to Kubernetes..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Not connected to a Kubernetes cluster"
    exit 1
fi

print_status "Connected to Kubernetes cluster: $(kubectl config current-context)"

# Deploy in order: ConfigMaps/Secrets first, then PVC, then services, then deployments
print_status "Creating ConfigMaps and Secrets..."
kubectl apply -f k8s/configmap.yaml

print_status "Creating PersistentVolumeClaim..."
kubectl apply -f k8s/pvc.yaml

print_status "Creating Redis deployment and service..."
kubectl apply -f k8s/deployment.yaml

print_status "Waiting for Redis to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis

print_status "Waiting for MCP Server to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mcp-server

print_status "Waiting for Gateway to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/gateway

print_status "Deployment completed successfully!"
echo ""
print_status "Service URLs:"
echo "  Gateway (NodePort): http://<node-ip>:30080"
echo "  Health Check: http://<node-ip>:30080/health"
echo ""
print_status "Default credentials: openwebui / openwebui"
echo ""
print_status "Check status with:"
echo "  kubectl get pods"
echo "  kubectl get svc"
echo "  kubectl logs -l app=gateway"
echo "  kubectl logs -l app=mcp-server"