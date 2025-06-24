# Running Minikube in WSL2 with GPU Passthrough (e.g., for CUDA)

You can absolutely run Minikube in WSL2 with GPU support – here’s how to set it up properly.

## ✅ Prerequisites

- **WSL2** enabled and properly configured
- An **NVIDIA GPU** with the latest Windows drivers
- **NVIDIA Container Toolkit** installed in WSL2
- **Docker** configured with the NVIDIA runtime inside WSL2
- **Minikube** installed (recommended drivers: `docker` or `none`)

## ⚙️ Setup Overview

### 1. Install NVIDIA Container Toolkit  
Follow the [official NVIDIA instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) to install `nvidia-docker2` and configure GPU support in WSL2.

### 2. Configure Docker Runtime
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 3. Start Minikube with GPU Support
```bash
minikube start --driver=docker --container-runtime=docker --gpus all
```

### 4. Enable the NVIDIA Device Plugin
```bash
minikube addons enable nvidia-device-plugin
#or
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/master/nvidia-device-plugin.yml
```

## 💡 Notes

- If using the `none` driver, you'll need `cri-dockerd` for newer Kubernetes versions.
- The `kvm` driver for true GPU passthrough requires IOMMU – not feasible under WSL2.
- Test GPU visibility with:
  
```bash
 docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
 ```