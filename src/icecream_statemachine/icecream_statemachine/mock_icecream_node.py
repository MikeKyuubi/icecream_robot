#!/usr/bin/env python3
"""
Mock Ice Cream Machine Node
=============================
Simulates the ice cream dispensing machine.
Different flavors take slightly different times (vanilla is fastest,
chocolate needs extra time to heat, mixed does both).

Subscribe: /icecream/cmd/dispense_icecream     (std_msgs/String)
Publish:   /icecream/done/icecream_dispensed   (std_msgs/String)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading
import time


class MockIceCreamNode(Node):

    # Simulated dispense times per flavor (seconds)
    DISPENSE_TIMES = {
        'vanilla':   4.0,
        'chocolate': 5.5,   # needs extra warm-up
        'mixed':     7.0,   # two passes
    }
    DEFAULT_DISPENSE_TIME = 5.0

    def __init__(self):
        super().__init__('mock_icecream_machine')

        self.pub_done = self.create_publisher(
            String, '/icecream/done/icecream_dispensed', 10)

        self.create_subscription(
            String, '/icecream/cmd/dispense_icecream', self._on_dispense_command, 10)

        self.get_logger().info('🍦 Mock ice cream machine ready.')

    def _on_dispense_command(self, msg: String):
        flavor = msg.data
        delay = self.DISPENSE_TIMES.get(flavor, self.DEFAULT_DISPENSE_TIME)
        self.get_logger().info(f'  [IceCream] Dispensing {flavor}... ({delay}s)')

        def _do_work():
            time.sleep(delay)

            done = String()
            done.data = 'ok'
            self.pub_done.publish(done)
            self.get_logger().info(f'  [IceCream] ✓ {flavor} dispensed!')

        threading.Thread(target=_do_work, daemon=True).start()


def main(args=None):
    rclpy.init(args=args)
    node = MockIceCreamNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
