from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

        Node(
            package='icecream_statemachine',
            executable='state_machine',
            name='icecream_state_machine',
            output='screen',
            emulate_tty=True,
        ),

        # Cobot node handles all motion AND publishes all done signals
        Node(
            package='icecream_statemachine',
            executable='cobot',
            name='cobot_node',
            output='screen',
            emulate_tty=True,
        ),

    ])
