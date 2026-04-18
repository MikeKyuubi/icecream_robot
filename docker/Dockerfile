# ── Base: NVIDIA L4T ROS2 Humble for JetPack 6.x (aarch64) ──────────────────
FROM dustynv/ros:humble-ros-base-l4t-r36.2.0

# ── Environment ───────────────────────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV ROS_DOMAIN_ID=0
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ENV WORKSPACE=/ros2_ws

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    # ROS2 MoveIt2
    ros-humble-moveit \
    ros-humble-moveit-ros-planning \
    ros-humble-moveit-ros-move-group \
    ros-humble-moveit-kinematics \
    ros-humble-trac-ik-kinematics-plugin \
    ros-humble-controller-manager \
    ros-humble-joint-trajectory-controller \
    ros-humble-joint-state-broadcaster \
    ros-humble-ros2-control \
    # Qt6 for dashboard
    qt6-base-dev \
    qt6-declarative-dev \
    qml6-module-qtquick \
    qml6-module-qtquick-controls \
    qml6-module-qtquick-layouts \
    libqt6svg6-dev \
    # Python
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    # Utilities
    git \
    udev \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ───────────────────────────────────────────────────────
RUN pip3 install --no-cache-dir \
    pymycobot \
    transforms3d \
    numpy

# ── Create workspace ──────────────────────────────────────────────────────────
WORKDIR ${WORKSPACE}
RUN mkdir -p src

# ── Copy packages ─────────────────────────────────────────────────────────────
COPY src/icecream_statemachine   ${WORKSPACE}/src/icecream_statemachine
COPY src/icecream_dashboard      ${WORKSPACE}/src/icecream_dashboard
COPY src/mycobot_ros2            ${WORKSPACE}/src/mycobot_ros2
COPY src/mycobot_ros2_humble     ${WORKSPACE}/src/mycobot_ros2_humble

# ── Install ROS dependencies ──────────────────────────────────────────────────
RUN . /opt/ros/humble/setup.sh && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y

# ── Build workspace ───────────────────────────────────────────────────────────
RUN . /opt/ros/humble/setup.sh && \
    colcon build \
        --packages-select \
            mycobot_description \
            pro450_moveit2 \
            icecream_statemachine \
            icecream_dashboard \
        --allow-overriding mycobot_description \
        --cmake-args -DCMAKE_BUILD_TYPE=Release \
    && rm -rf build log

# ── Setup entrypoint ──────────────────────────────────────────────────────────
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
