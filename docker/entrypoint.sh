#!/bin/bash
set -e

# Source ROS2
source /opt/ros/humble/setup.bash

# Source workspace
if [ -f /ros2_ws/install/setup.bash ]; then
    source /ros2_ws/install/setup.bash
fi

# USB serial device permissions
if [ -e /dev/ttyUSB0 ]; then
    chmod 666 /dev/ttyUSB0
fi
if [ -e /dev/ttyACM0 ]; then
    chmod 666 /dev/ttyACM0
fi

exec "$@"
