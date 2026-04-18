#!/usr/bin/env python3
"""
Real Cobot Node — myCobot 280/450
Handles all 3 phases of the ice cream serving sequence.
Each phase moves the arm to the appropriate position.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest, WorkspaceParameters,
    Constraints, JointConstraint
)
import threading
import time


class CobotNode(Node):

    JOINT_NAMES = [
        'joint1', 'joint2', 'joint3',
        'joint4', 'joint5', 'joint6',
    ]

    # ── Waypoints per phase ───────────────────────────────────────────────────
    # Each phase: list of (name, [j1..j6], duration_hint)
    GRAB_CUP_WAYPOINTS = [
        ('home',              [0.0,  0.0,  0.0,  0.0,  0.0,  0.0], 2.0),
        ('approach_dispenser',[0.8, -0.3,  0.3, -0.2,  0.3,  0.0], 2.5),
        ('grab_cup',          [0.8, -0.5,  0.6, -0.3,  0.3,  0.0], 1.5),
    ]

    GET_ICECREAM_WAYPOINTS = [
        ('approach_nozzle',   [0.0, -0.4,  0.7, -0.4,  0.0,  0.0], 2.5),
        ('under_nozzle',      [0.0, -0.3,  1.0, -0.7,  0.0,  0.0], 2.0),
        ('hold_for_fill',     [0.0, -0.3,  1.0, -0.7,  0.0,  0.0], 1.0),
    ]

    SERVE_WAYPOINTS = [
        ('lift_from_nozzle',  [0.0, -0.5,  0.8, -0.5,  0.0,  0.0], 2.0),
        ('serving_position',  [1.0, -0.5,  0.5, -0.3,  0.5,  0.0], 2.5),
        ('present_to_customer',[1.0, -0.3,  0.4, -0.2,  0.5,  0.0], 1.5),
        ('home',              [0.0,  0.0,  0.0,  0.0,  0.0,  0.0], 2.0),
    ]

    def __init__(self):
        super().__init__('cobot_node')

        self._cb_group = ReentrantCallbackGroup()
        self._moveit_ready = False

        # Publishers — done confirmations
        self.pub_cup_done      = self.create_publisher(String, '/icecream/done/cup_grabbed', 10)
        self.pub_icecream_done = self.create_publisher(String, '/icecream/done/icecream_dispensed', 10)
        self.pub_serve_done    = self.create_publisher(String, '/icecream/done/served', 10)

        # Subscribers — commands from state machine
        self.create_subscription(String, '/icecream/cmd/grab_cup',
            self._on_grab_cup, 10, callback_group=self._cb_group)
        self.create_subscription(String, '/icecream/cmd/dispense_icecream',
            self._on_get_icecream, 10, callback_group=self._cb_group)
        self.create_subscription(String, '/icecream/cmd/serve',
            self._on_serve, 10, callback_group=self._cb_group)

        # MoveIt2 action client
        self._move_client = ActionClient(
            self, MoveGroup, '/move_action',
            callback_group=self._cb_group)

        threading.Thread(target=self._wait_for_moveit, daemon=True).start()

    def _wait_for_moveit(self):
        self.get_logger().info('🦾 Cobot node starting — waiting for MoveIt2...')
        available = self._move_client.wait_for_server(timeout_sec=60.0)
        if available:
            self._moveit_ready = True
            self.get_logger().info('🦾 Cobot node ready. MoveIt2 connected.')
        else:
            self.get_logger().error('🦾 MoveIt2 not available after 60s — using fallback timing.')

    # ── Phase handlers ────────────────────────────────────────────────────────
    def _on_grab_cup(self, msg: String):
        flavor = msg.data
        self.get_logger().info(f'  [Cobot] Phase 1: Grabbing cup for {flavor}')
        threading.Thread(
            target=self._execute_phase,
            args=(self.GRAB_CUP_WAYPOINTS, self.pub_cup_done, 'grab_cup', flavor),
            daemon=True).start()

    def _on_get_icecream(self, msg: String):
        flavor = msg.data
        self.get_logger().info(f'  [Cobot] Phase 2: Getting {flavor} ice cream')
        threading.Thread(
            target=self._execute_phase,
            args=(self.GET_ICECREAM_WAYPOINTS, self.pub_icecream_done, 'get_icecream', flavor),
            daemon=True).start()

    def _on_serve(self, msg: String):
        flavor = msg.data
        self.get_logger().info(f'  [Cobot] Phase 3: Serving {flavor}')
        threading.Thread(
            target=self._execute_phase,
            args=(self.SERVE_WAYPOINTS, self.pub_serve_done, 'serve', flavor),
            daemon=True).start()

    # ── Execution ─────────────────────────────────────────────────────────────
    def _execute_phase(self, waypoints, done_pub, phase_name, flavor):
        total = len(waypoints)
        for i, (name, positions, duration) in enumerate(waypoints):
            self.get_logger().info(
                f'  [Cobot] [{phase_name}] Waypoint {i+1}/{total}: {name}')

            if self._moveit_ready:
                success = self._move_to_joint_positions(positions, duration)
                if not success:
                    self.get_logger().warn(
                        f'  [Cobot] [{phase_name}] Waypoint {name} failed, continuing...')
            else:
                # Fallback: just sleep the duration
                time.sleep(duration)

            time.sleep(0.2)

        done = String()
        done.data = 'ok'
        done_pub.publish(done)
        self.get_logger().info(f'  [Cobot] [{phase_name}] ✓ Phase complete!')

    def _move_to_joint_positions(self, positions: list, duration: float) -> bool:
        constraints = Constraints()
        for name, pos in zip(self.JOINT_NAMES, positions):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = pos
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        request = MotionPlanRequest()
        request.group_name = 'arm_group'
        request.goal_constraints.append(constraints)
        request.num_planning_attempts = 5
        request.allowed_planning_time = 5.0
        request.max_velocity_scaling_factor = 0.5
        request.max_acceleration_scaling_factor = 0.5

        workspace = WorkspaceParameters()
        workspace.header.frame_id = 'base_link'
        workspace.min_corner.x = -1.0
        workspace.min_corner.y = -1.0
        workspace.min_corner.z = -1.0
        workspace.max_corner.x = 1.0
        workspace.max_corner.y = 1.0
        workspace.max_corner.z = 1.0
        request.workspace_parameters = workspace

        goal = MoveGroup.Goal()
        goal.request = request
        goal.planning_options.plan_only = False
        goal.planning_options.replan = True
        goal.planning_options.replan_attempts = 3

        future = self._move_client.send_goal_async(goal)

        start = time.time()
        while not future.done():
            time.sleep(0.05)
            if time.time() - start > 10.0:
                self.get_logger().error('  [Cobot] Timeout waiting for goal acceptance')
                return False

        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error('  [Cobot] Goal rejected')
            return False

        result_future = goal_handle.get_result_async()
        start = time.time()
        while not result_future.done():
            time.sleep(0.1)
            if time.time() - start > 30.0:
                self.get_logger().error('  [Cobot] Timeout waiting for result')
                return False

        result = result_future.result()
        if result and result.result.error_code.val == 1:
            return True

        code = result.result.error_code.val if result else 'timeout'
        self.get_logger().warn(f'  [Cobot] MoveIt2 error code: {code}')
        return False


def main(args=None):
    rclpy.init(args=args)
    node = CobotNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
