#!/usr/bin/env python3
"""
Mock Cup Dispenser Node
========================
Simulates a cup dispenser.
Receives a grab command, waits a realistic delay, then confirms done.

Subscribe: /icecream/cmd/grab_cup        (std_msgs/String)
Publish:   /icecream/done/cup_grabbed    (std_msgs/String)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading
import time


class MockDispenserNode(Node):

    # Simulated time to physically grab a cup (seconds)
    GRAB_DELAY = 3.0

    def __init__(self):
        super().__init__('mock_dispenser')

        self.pub_done = self.create_publisher(
            String, '/icecream/done/cup_grabbed', 10)

        self.create_subscription(
            String, '/icecream/cmd/grab_cup', self._on_grab_command, 10)

        self.get_logger().info('🥤 Mock cup dispenser ready.')

    def _on_grab_command(self, msg: String):
        flavor = msg.data
        self.get_logger().info(f'  [Dispenser] Grabbing cup for: {flavor}')

        def _do_work():
            self.get_logger().info(f'  [Dispenser] Dispensing cup... ({self.GRAB_DELAY}s)')
            time.sleep(self.GRAB_DELAY)

            done = String()
            done.data = 'ok'
            self.pub_done.publish(done)
            self.get_logger().info('  [Dispenser] ✓ Cup grabbed!')

        threading.Thread(target=_do_work, daemon=True).start()


def main(args=None):
    rclpy.init(args=args)
    node = MockDispenserNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
