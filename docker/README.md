# Ice Cream Robot — Docker Deployment
## Jetson Orin Nano Super (JetPack 6.x, Ubuntu 22.04, aarch64)

## Folder structure
```
your_project/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   ├── icecream_robot.launch.py   ← copy to icecream_statemachine/launch/
│   └── README.md
└── src/
    ├── icecream_statemachine/
    ├── icecream_dashboard/
    ├── mycobot_ros2/
    └── mycobot_ros2_humble/
```

## Setup on Jetson

### 1. Install Docker
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Install NVIDIA Container Toolkit
```bash
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 3. Copy your workspace to Jetson
```bash
# From your dev PC:
rsync -av --exclude='build' --exclude='install' --exclude='log' \
  ~/ros2_qt_ws/ jetson@<JETSON_IP>:~/ros2_qt_ws/
```

### 4. Copy the launch file
```bash
cp docker/icecream_robot.launch.py \
   src/icecream_statemachine/launch/
```

### 5. Allow X11 display (for Qt dashboard)
```bash
xhost +local:docker
```

### 6. Build the Docker image
```bash
cd ~/ros2_qt_ws
docker compose -f docker/docker-compose.yml build
```
This will take 10-20 minutes on first build.

### 7. Connect the myCobot 450
```bash
# Check which port it's on
ls /dev/ttyUSB* /dev/ttyACM*
```
Update docker-compose.yml if port is different from /dev/ttyUSB0.

### 8. Run
```bash
docker compose -f docker/docker-compose.yml up
```

## Useful commands
```bash
# Run in background
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose -f docker/docker-compose.yml logs -f

# Shell into container
docker exec -it icecream_robot bash

# Stop
docker compose -f docker/docker-compose.yml down

# Rebuild after code changes
docker compose -f docker/docker-compose.yml build --no-cache
```

## Troubleshooting

**Qt dashboard not showing:**
```bash
xhost +local:docker
export DISPLAY=:0
```

**myCobot not found:**
```bash
# Check port
ls /dev/ttyUSB* /dev/ttyACM*
# Update devices in docker-compose.yml
```

**Permission denied on serial port:**
```bash
sudo chmod 666 /dev/ttyUSB0
# or add user to dialout group
sudo usermod -aG dialout $USER
```
