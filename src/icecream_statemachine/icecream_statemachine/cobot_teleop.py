#!/usr/bin/env python3
"""
myCobot 450 Keyboard Teleop
=============================
Cartesian + Joint mode keyboard control for waypoint discovery.

CARTESIAN MODE (default):
  W / S    →  X+ / X-  (forward/back)
  A / D    →  Y+ / Y-  (left/right)
  R / F    →  Z+ / Z-  (up/down)
  I / K    →  Roll+  / Roll-
  J / L    →  Pitch+ / Pitch-
  U / O    →  Yaw+   / Yaw-

JOINT MODE:
  1-6      →  Select joint
  + / =    →  Rotate selected joint +increment
  - / _    →  Rotate selected joint -increment
  [ / ]    →  Decrease / Increase step size

COMMON:
  M        →  Toggle Cartesian / Joint mode
  P        →  Print current joint states
  H        →  Move to ready position (non-singular)
  Space    →  Stop
  Q        →  Quit
"""

import sys
import threading
import select
import termios
import tty
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from moveit_msgs.srv import ServoCommandType
from std_srvs.srv import SetBool
from rclpy.action import ActionClient
from builtin_interfaces.msg import Duration


JOINT_NAMES = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']

# Non-singular ready position (arm slightly bent, away from singularity)
READY_POSITIONS = [0.0, -0.5, 0.8, -0.3, 0.0, 0.0]
HOME_POSITIONS   = [0.0,  0.0, 0.0,  0.0, 0.0, 0.0]

CARTESIAN_BINDINGS = {
    'w': ( 1,  0,  0,  0,  0,  0),  # X+
    's': (-1,  0,  0,  0,  0,  0),  # X-
    'a': ( 0,  1,  0,  0,  0,  0),  # Y+
    'd': ( 0, -1,  0,  0,  0,  0),  # Y-
    'r': ( 0,  0,  1,  0,  0,  0),  # Z+
    'f': ( 0,  0, -1,  0,  0,  0),  # Z-
    'i': ( 0,  0,  0,  1,  0,  0),  # Roll+
    'k': ( 0,  0,  0, -1,  0,  0),  # Roll-
    'j': ( 0,  0,  0,  0,  1,  0),  # Pitch+
    'l': ( 0,  0,  0,  0, -1,  0),  # Pitch-
    'u': ( 0,  0,  0,  0,  0,  1),  # Yaw+
    'o': ( 0,  0,  0,  0,  0, -1),  # Yaw-
}

MENU = """
╔══════════════════════════════════════════════════════╗
║         myCobot 450 Keyboard Teleop                  ║
╠══════════════════════════════════════════════════════╣
║  CARTESIAN MODE                                      ║
║   W/S  → X+/X-    A/D  → Y+/Y-    R/F → Z+/Z-      ║
║   I/K  → Roll     J/L  → Pitch    U/O → Yaw         ║
╠══════════════════════════════════════════════════════╣
║  JOINT MODE  (servo paused — no snap-back)           ║
║   1-6  → Select joint                               ║
║   +/=  → Joint+   -/_  → Joint-                     ║
║   [/]  → Decrease/Increase step size                ║
╠══════════════════════════════════════════════════════╣
║  COMMON                                              ║
║   M    → Toggle mode    P → Print joints             ║
║   H    → Ready pose     G → Go to true home          ║
║   </> → Speed-/Speed+   Space → Stop                ║
║   Q    → Quit                                        ║
╚══════════════════════════════════════════════════════╝
"""


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1) if rlist else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class CobotTeleop(Node):

    def __init__(self):
        super().__init__('cobot_teleop')

        self.mode = 'cartesian'
        self.selected_joint = 0
        self.joint_step = 0.05
        self.cartesian_speed = 0.05
        self.current_joints = [0.0] * 6

        # Publishers
        self.twist_pub = self.create_publisher(
            TwistStamped, '/servo_node/delta_twist_cmds', 10)

        # Action client for joint trajectory
        self._joint_client = ActionClient(
            self, FollowJointTrajectory,
            '/arm_group_controller/follow_joint_trajectory')

        # Service clients
        self._servo_type_client = self.create_client(
            ServoCommandType, '/servo_node/switch_command_type')
        self._servo_pause_client = self.create_client(
            SetBool, '/servo_node/pause_servo')

        # Joint state subscriber
        self.create_subscription(
            JointState, '/joint_states', self._on_joint_states, 10)

        self.get_logger().info('Teleop node ready.')

        # Auto-enable cartesian mode
        threading.Thread(target=self._activate_cartesian, daemon=True).start()

    # ── Joint states ──────────────────────────────────────────────────────────
    def _on_joint_states(self, msg: JointState):
        for i, name in enumerate(JOINT_NAMES):
            if name in msg.name:
                self.current_joints[i] = msg.position[msg.name.index(name)]

    # ── Servo control ─────────────────────────────────────────────────────────
    def _activate_cartesian(self):
        """Resume servo + switch to twist command type."""
        # Resume servo
        if self._servo_pause_client.wait_for_service(timeout_sec=5.0):
            req = SetBool.Request()
            req.data = False  # False = resume
            self._servo_pause_client.call_async(req)
            time.sleep(0.2)

        # Switch to twist mode
        if self._servo_type_client.wait_for_service(timeout_sec=5.0):
            req = ServoCommandType.Request()
            req.command_type = 1  # TwistStamped
            self._servo_type_client.call_async(req)
            time.sleep(0.2)
            print('  ✓ Cartesian servo mode active.')

    def _pause_servo(self):
        """Pause servo so it doesn't fight joint trajectory commands."""
        if self._servo_pause_client.wait_for_service(timeout_sec=2.0):
            req = SetBool.Request()
            req.data = True  # True = pause
            self._servo_pause_client.call_async(req)

    # ── Movement ──────────────────────────────────────────────────────────────
    def send_cartesian(self, vx, vy, vz, wx, wy, wz):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base'
        msg.twist.linear.x  = vx * self.cartesian_speed
        msg.twist.linear.y  = vy * self.cartesian_speed
        msg.twist.linear.z  = vz * self.cartesian_speed
        msg.twist.angular.x = wx * self.cartesian_speed
        msg.twist.angular.y = wy * self.cartesian_speed
        msg.twist.angular.z = wz * self.cartesian_speed
        self.twist_pub.publish(msg)

    def stop_cartesian(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base'
        self.twist_pub.publish(msg)

    def send_joint_delta(self, delta: float):
        target = list(self.current_joints)
        target[self.selected_joint] += delta
        limits = [2.8274, 2.1816, 2.6878, 2.8274, 2.8274, 2.8797]
        target[self.selected_joint] = max(
            -limits[self.selected_joint],
            min(limits[self.selected_joint], target[self.selected_joint]))
        self._send_joint_goal(target, duration_sec=0.8)

    def send_ready(self):
        """Move to non-singular ready pose."""
        self._send_joint_goal(READY_POSITIONS, duration_sec=3.0)

    def send_home(self):
        self._send_joint_goal(HOME_POSITIONS, duration_sec=3.0)

    def _send_joint_goal(self, positions, duration_sec=2.0):
        if not self._joint_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn('Joint action server not available')
            return
        traj = JointTrajectory()
        traj.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))
        traj.points = [point]
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = traj
        self._joint_client.send_goal_async(goal)

    def print_joints(self):
        print('\n' + '─' * 55)
        print('  Current joint positions (copy to cobot_node.py):')
        print('─' * 55)
        vals = ', '.join(f'{v:.4f}' for v in self.current_joints)
        print(f'  [{vals}]')
        print('─' * 55 + '\n')


def main():
    rclpy.init()
    node = CobotTeleop()

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    settings = termios.tcgetattr(sys.stdin)
    print(MENU)
    print(f'  Mode: CARTESIAN  |  Speed: {node.cartesian_speed} m/s  '
          f'|  Step: {node.joint_step:.3f} rad')
    print(f'  Speed: {node.cartesian_speed} m/s  |  Use < / > to change speed')
    # Tip: Press F to move down from singularity first!\n')

    try:
        while rclpy.ok():
            key = get_key(settings)

            if not key:
                if node.mode == 'cartesian':
                    node.stop_cartesian()
                continue

            key_lower = key.lower()

            # ── Quit ─────────────────────────────────────────────────────────
            if key_lower == 'q':
                print('\nQuitting...')
                break

            # ── Toggle mode ──────────────────────────────────────────────────
            elif key_lower == 'm':
                if node.mode == 'cartesian':
                    node.mode = 'joint'
                    node.stop_cartesian()
                    threading.Thread(target=node._pause_servo, daemon=True).start()
                    print('  Mode: JOINT  (servo paused)')
                else:
                    node.mode = 'cartesian'
                    threading.Thread(target=node._activate_cartesian, daemon=True).start()
                    print('  Mode: CARTESIAN  (servo resuming...)')

            # ── Print joints ─────────────────────────────────────────────────
            elif key_lower == 'p':
                node.print_joints()

            # ── Ready pose (non-singular) ─────────────────────────────────────
            elif key_lower == 'h':
                print('  Moving to ready pose (non-singular)...')
                node.stop_cartesian()
                threading.Thread(target=node._pause_servo, daemon=True).start()
                node.send_ready()
                time.sleep(3.5)
                threading.Thread(target=node._activate_cartesian, daemon=True).start()
                node.mode = 'cartesian'

            # ── True home ────────────────────────────────────────────────────
            elif key_lower == 'g':
                print('  Moving to true home (0,0,0,0,0,0)...')
                node.stop_cartesian()
                threading.Thread(target=node._pause_servo, daemon=True).start()
                node.send_home()
                time.sleep(3.5)
                threading.Thread(target=node._activate_cartesian, daemon=True).start()
                node.mode = 'cartesian'

            # ── Stop ─────────────────────────────────────────────────────────
            elif key == ' ':
                node.stop_cartesian()
                print('  Stopped.')

            # ── Joint selection ───────────────────────────────────────────────
            elif key in '123456':
                node.selected_joint = int(key) - 1
                print(f'  Selected: joint{key}  '
                      f'(current: {node.current_joints[node.selected_joint]:.4f} rad)')

            # ── Step size ─────────────────────────────────────────────────────
            elif key == '[':
                node.joint_step = max(0.01, node.joint_step - 0.01)
                print(f'  Step: {node.joint_step:.3f} rad')

            elif key == '<':
                node.cartesian_speed = max(0.01, round(node.cartesian_speed - 0.02, 2))
                print(f'  Speed: {node.cartesian_speed} m/s')

            elif key == '>':
                node.cartesian_speed = min(0.5, round(node.cartesian_speed + 0.02, 2))
                print(f'  Speed: {node.cartesian_speed} m/s')

            elif key == ']':
                node.joint_step = min(0.2, node.joint_step + 0.01)
                print(f'  Step: {node.joint_step:.3f} rad')

            # ── Speed control ─────────────────────────────────────────────────
            elif key == '<':
                node.cartesian_speed = max(0.01, round(node.cartesian_speed - 0.02, 2))
                print(f'  Speed: {node.cartesian_speed} m/s')

            elif key == '>':
                node.cartesian_speed = min(0.5, round(node.cartesian_speed + 0.02, 2))
                print(f'  Speed: {node.cartesian_speed} m/s')

            # ── Cartesian movement ────────────────────────────────────────────────
            elif node.mode == 'cartesian' and key_lower in CARTESIAN_BINDINGS:
                node.send_cartesian(*CARTESIAN_BINDINGS[key_lower])

            # ── Joint movement ────────────────────────────────────────────────
            elif node.mode == 'joint':
                if key in ('+', '='):
                    node.send_joint_delta(+node.joint_step)
                    print(f'  joint{node.selected_joint+1}: '
                          f'{node.current_joints[node.selected_joint]:.4f} rad')
                elif key in ('-', '_'):
                    node.send_joint_delta(-node.joint_step)
                    print(f'  joint{node.selected_joint+1}: '
                          f'{node.current_joints[node.selected_joint]:.4f} rad')

    except KeyboardInterrupt:
        pass
    finally:
        node.stop_cartesian()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()# speed patch applied below main() — ignore
