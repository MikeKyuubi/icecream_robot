#!/usr/bin/env python3
"""
Test Ice Cream Swirl Motion — IK-based Cartesian circle
=========================================================
Generates a circle of poses around the nozzle position.
The cup rim stays fixed at the nozzle XYZ.
The orientation tilts 30° at the start and decrements proportionally
to 0° as it approaches 720° rotation — like settling ice cream into the cup.

Run with:
  source ~/ros2_qt_ws/install/setup.bash
  python3 test_swirl.py
"""

import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from moveit_msgs.msg import PositionIKRequest, RobotState
from moveit_msgs.srv import GetPositionIK
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PoseStamped, Pose
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from tf_transformations import quaternion_from_euler, quaternion_multiply
import time


JOINT_NAMES = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']

# Nozzle position — cup rim is HERE, stays fixed
NOZZLE_XYZ    = [0.269, -0.084, 0.441]

# Starting joints when cup is under nozzle
NOZZLE_JOINTS = [0.0, -0.342, -1.435, 1.782, 0.0, 0.0]

# Swirl parameters
TILT_DEG   = 30.0   # max tilt at start of swirl
ROTATIONS  = 2      # full circles (720°)
DURATION   = 6.0    # total swirl time in seconds
STEPS      = 36     # waypoints per rotation (10° each)


def make_trajectory(positions, duration_sec):
    traj = JointTrajectory()
    traj.joint_names = JOINT_NAMES
    pt = JointTrajectoryPoint()
    pt.positions = list(positions)
    pt.time_from_start = Duration(
        sec=int(duration_sec),
        nanosec=int((duration_sec % 1) * 1e9))
    traj.points = [pt]
    return traj


class SwirlTest(Node):

    def __init__(self):
        super().__init__('swirl_test')

        self._traj_client = ActionClient(
            self, FollowJointTrajectory,
            '/arm_group_controller/follow_joint_trajectory')

        self._ik_client = self.create_client(
            GetPositionIK, '/compute_ik')

        self.current_joints = list(NOZZLE_JOINTS)
        self.create_subscription(
            JointState, '/joint_states', self._on_joints, 10)

    def _on_joints(self, msg):
        for i, name in enumerate(JOINT_NAMES):
            if name in msg.name:
                self.current_joints[i] = msg.position[msg.name.index(name)]

    def _send_traj(self, traj, wait_sec):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj
        future = self._traj_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        gh = future.result()
        if not gh or not gh.accepted:
            print('  Rejected!')
            return False
        time.sleep(wait_sec + 0.3)
        return True

    def _solve_ik(self, pose: Pose, seed_joints: list):
        if not self._ik_client.wait_for_service(timeout_sec=2.0):
            print('  IK service not available')
            return None

        req = GetPositionIK.Request()
        req.ik_request.group_name = 'arm_group'
        req.ik_request.avoid_collisions = False
        req.ik_request.timeout.sec = 0
        req.ik_request.timeout.nanosec = 50_000_000

        js = JointState()
        js.name = JOINT_NAMES
        js.position = list(seed_joints)
        rs = RobotState()
        rs.joint_state = js
        req.ik_request.robot_state = rs

        ps = PoseStamped()
        ps.header.frame_id = 'base'
        ps.pose = pose
        req.ik_request.pose_stamped = ps
        req.ik_request.ik_link_name = 'link6'

        future = self._ik_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)

        result = future.result()
        if result and result.error_code.val == 1:
            js = result.solution.joint_state
            joints = []
            for name in JOINT_NAMES:
                if name in js.name:
                    joints.append(js.position[js.name.index(name)])
            return joints
        return None

    def generate_swirl_trajectory(self):
        tilt_rad = math.radians(TILT_DEG)
        total_steps = STEPS * ROTATIONS
        points = []
        seed = list(NOZZLE_JOINTS)
        failed = 0

        print(f'  Solving IK for {total_steps} waypoints...')

        for i in range(total_steps + 1):
            t = i / total_steps

            # ── Ramp: quick rise, then linear decrement to 0 ─────────────
            # t=0.0  → ramp=0.0  (start upright)
            # t=0.1  → ramp=1.0  (full 30° tilt reached quickly)
            # t=0.5  → ramp=0.56 (just past halfway, still leaning)
            # t=1.0  → ramp=0.0  (back upright, centered under nozzle)
            if t < 0.1:
                ramp = t / 0.1          # quick ramp up in first 10%
            else:
                ramp = 1.0 - ((t - 0.1) / 0.9)  # linear decrement to 0

            angle = t * 2.0 * math.pi * ROTATIONS

            pose = Pose()

            # Position: cup rim stays FIXED at nozzle
            pose.position.x = NOZZLE_XYZ[0]
            pose.position.y = NOZZLE_XYZ[1]
            pose.position.z = NOZZLE_XYZ[2]

            # Orientation: tilt decrements as rotation progresses
            tilt = tilt_rad * ramp
            tilt_x = tilt * math.cos(angle)
            tilt_y = tilt * math.sin(angle)

            q_base = [0.0, -0.002, 0.0, 1.0]
            q_tilt_x = quaternion_from_euler(tilt_x, 0.0, 0.0)
            q_tilt_y = quaternion_from_euler(0.0, tilt_y, 0.0)
            q_tilt = quaternion_multiply(q_tilt_x, q_tilt_y)
            q_final = quaternion_multiply(q_base, q_tilt)

            pose.orientation.x = q_final[0]
            pose.orientation.y = q_final[1]
            pose.orientation.z = q_final[2]
            pose.orientation.w = q_final[3]

            joints = self._solve_ik(pose, seed)

            if joints:
                seed = joints
                elapsed = t * DURATION
                pt = JointTrajectoryPoint()
                pt.positions = joints
                pt.time_from_start = Duration(
                    sec=int(elapsed),
                    nanosec=int((elapsed % 1) * 1e9))
                points.append(pt)
            else:
                failed += 1

        # End: return upright at nozzle
        pt = JointTrajectoryPoint()
        pt.positions = list(NOZZLE_JOINTS)
        pt.time_from_start = Duration(sec=int(DURATION + 2.0), nanosec=0)
        points.append(pt)

        print(f'  ✓ {len(points)} waypoints  ({failed} failed/skipped)')
        return points

    def run(self):
        print('Waiting for action server...')
        self._traj_client.wait_for_server()
        print('Connected!\n')

        print('Step 1: Moving to nozzle position...')
        traj = make_trajectory(NOZZLE_JOINTS, duration_sec=3.0)
        if not self._send_traj(traj, wait_sec=3.0):
            return
        print('  ✓ At nozzle\n')

        print('Step 2: Computing swirl trajectory...')
        print(f'  30° tilt → decrements to 0° over 720° rotation')
        points = self.generate_swirl_trajectory()

        if len(points) < 5:
            print('  ✗ Too few waypoints — check IK service')
            return

        print(f'\nStep 3: Executing swirl...')
        print('  Watch RViz!\n')

        swirl_traj = JointTrajectory()
        swirl_traj.joint_names = JOINT_NAMES
        swirl_traj.points = points

        if not self._send_traj(swirl_traj, wait_sec=DURATION + 2.5):
            return
        print('  ✓ Swirl complete!\n')

        print('Step 4: Returning to nozzle position...')
        traj = make_trajectory(NOZZLE_JOINTS, duration_sec=2.0)
        self._send_traj(traj, wait_sec=2.0)
        print('  ✓ Done!')


def main():
    rclpy.init()
    node = SwirlTest()
    time.sleep(2.0)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()