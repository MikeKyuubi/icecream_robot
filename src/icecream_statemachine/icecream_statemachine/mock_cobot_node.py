#!/usr/bin/env python3
"""
Mock Cobot Node
================
Simulates the myCobot 450 performing the serving motion.
Logs each simulated waypoint so you can see what MoveIt2
will eventually execute when the real robot is connected.

Simulated motion sequence:
  1. Move to cup pickup position
  2. Close gripper
  3. Move to ice cream machine
  4. Move to serving window
  5. Open gripper / release
  6. Return to home

Subscribe: /icecream/cmd/serve      (std_msgs/String)
Publish:   /icecream/done/served    (std_msgs/String)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading
import time


class MockCobotNode(Node):

    # Simulated waypoints with durations (name, seconds)
    WAYPOINTS = [
        ('Moving to home position',          1.5),
        ('Moving to cup pickup position',    2.0),
        ('Closing gripper',                  0.8),
        ('Lifting cup',                      1.0),
        ('Moving to ice cream machine',      2.5),
        ('Positioning cup under nozzle',     1.0),
        ('Waiting for ice cream...',         0.5),   # ice cream node handles actual wait
        ('Moving to serving window',         2.0),
        ('Presenting cup to customer',       1.0),
        ('Opening gripper / releasing cup',  0.8),
        ('Returning to home position',       2.0),
    ]

    def __init__(self):
        super().__init__('mock_cobot')

        self.pub_done = self.create_publisher(
            String, '/icecream/done/served', 10)

        self.create_subscription(
            String, '/icecream/cmd/serve', self._on_serve_command, 10)

        self.get_logger().info('🦾 Mock cobot (myCobot 450) ready.')

    def _on_serve_command(self, msg: String):
        flavor = msg.data
        self.get_logger().info(f'  [Cobot] Starting serve sequence for: {flavor}')

        def _do_work():
            total = sum(d for _, d in self.WAYPOINTS)
            self.get_logger().info(f'  [Cobot] Executing {len(self.WAYPOINTS)} waypoints (~{total:.1f}s total)')

            for waypoint, duration in self.WAYPOINTS:
                self.get_logger().info(f'  [Cobot]   ▸ {waypoint} ({duration}s)')
                time.sleep(duration)

            done = String()
            done.data = 'ok'
            self.pub_done.publish(done)
            self.get_logger().info('  [Cobot] ✓ Serve complete!')

        threading.Thread(target=_do_work, daemon=True).start()


def main(args=None):
    rclpy.init(args=args)
    node = MockCobotNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
