#!/usr/bin/env python3
"""
Jetson Production Launch File
==============================
Launches the full ice cream robot stack on real hardware.
No Gazebo, no simulation — real myCobot 450 via USB.

Usage inside Docker:
  ros2 launch icecream_statemachine icecream_robot.launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    pkg_pro450 = FindPackageShare('pro450_moveit2').find('pro450_moveit2')

    moveit_config = (
        MoveItConfigsBuilder("firefighter", package_name="pro450_moveit2")
        .to_moveit_configs()
    )

    # ── Robot State Publisher ─────────────────────────────────────────────────
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
        ]
    )

    # ── MoveIt2 move_group ────────────────────────────────────────────────────
    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict()]
    )

    # ── State machine ─────────────────────────────────────────────────────────
    state_machine = Node(
        package='icecream_statemachine',
        executable='state_machine',
        name='icecream_state_machine',
        output='screen'
    )

    # ── Cobot node (real hardware) ────────────────────────────────────────────
    cobot_node = Node(
        package='icecream_statemachine',
        executable='cobot',
        name='cobot_node',
        output='screen',
        parameters=[{
            'use_real_hardware': True,
            'serial_port': '/dev/ttyUSB0',
            'baud_rate': 115200,
        }]
    )

    # ── Qt Dashboard ──────────────────────────────────────────────────────────
    dashboard = Node(
        package='icecream_dashboard',
        executable='icecream_dashboard',
        name='icecream_dashboard',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        TimerAction(period=2.0,  actions=[move_group]),
        TimerAction(period=5.0,  actions=[state_machine]),
        TimerAction(period=5.0,  actions=[cobot_node]),
        TimerAction(period=6.0,  actions=[dashboard]),
    ])
