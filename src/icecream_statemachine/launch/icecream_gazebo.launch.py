#!/usr/bin/env python3
"""
Ice Cream Station Launch File — myCobot 450 in Gazebo + Servo
"""

import os
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    pkg_ros_gz_sim = FindPackageShare('ros_gz_sim').find('ros_gz_sim')
    pkg_icecream   = FindPackageShare('icecream_statemachine').find('icecream_statemachine')
    pkg_pro450     = FindPackageShare('pro450_moveit2').find('pro450_moveit2')
    pkg_gz_control = FindPackageShare('gz_ros2_control').find('gz_ros2_control')

    world_file = os.path.join(pkg_icecream, 'worlds', 'icecream_station.world')
    servo_config = os.path.join(pkg_pro450, 'config', 'servo_config_450.yaml')

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Launch RViz')
    use_rviz = LaunchConfiguration('use_rviz')

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
            {'use_sim_time': True}
        ]
    )

    # ── Static transform ──────────────────────────────────────────────────────
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--qx', '0', '--qy', '0', '--qz', '0', '--qw', '1',
                   '--frame-id', 'world',
                   '--child-frame-id', 'base'],
        output='screen'
    )

    # ── Set GZ plugin path ────────────────────────────────────────────────────
    set_gz_resource_path = AppendEnvironmentVariable(
        'GZ_SIM_SYSTEM_PLUGIN_PATH',
        os.path.join(pkg_gz_control, 'lib')
    )

    # ── Gazebo ────────────────────────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments=[('gz_args', f' -r -v 3 {world_file}')])

    # ── Clock bridge ─────────────────────────────────────────────────────────
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # ── Spawn robot ───────────────────────────────────────────────────────────
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'mycobot_450',
            '-allow_renaming', 'true',
            '-x', '0.0', '-y', '0.0', '-z', '0.05',
        ]
    )

    # ── Controllers ───────────────────────────────────────────────────────────
    spawn_jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    spawn_arm = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_group_controller', '--controller-manager', '/controller_manager'],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # ── MoveIt2 move_group ────────────────────────────────────────────────────
    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            moveit_config.to_dict(),
            {'use_sim_time': True}
        ]
    )

    # ── Servo node ────────────────────────────────────────────────────────────
    servo_node = Node(
        package='moveit_servo',
        executable='servo_node',
        name='servo_node',
        output='screen',
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            servo_config,
            {'use_sim_time': True}
        ]
    )

    # ── RViz ─────────────────────────────────────────────────────────────────
    rviz_config = os.path.join(pkg_pro450, 'config', 'moveit.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            {'use_sim_time': True}
        ],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        declare_use_rviz,
        set_gz_resource_path,
        static_tf,
        robot_state_publisher,
        gazebo,
        gz_bridge,
        TimerAction(period=2.0,  actions=[spawn_robot]),
        TimerAction(period=8.0,  actions=[spawn_jsb, spawn_arm]),
        TimerAction(period=10.0, actions=[move_group]),
        TimerAction(period=12.0, actions=[servo_node]),
        TimerAction(period=13.0, actions=[rviz]),
    ])