#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading
import time


class IceCreamStateMachine(Node):

    def __init__(self):
        super().__init__('icecream_state_machine')

        self.current_state = 'idle'
        self.active_flavor = ''
        self.busy = False
        self._done_event = threading.Event()
        self._expected_done = None

        self.pub_state    = self.create_publisher(String, '/icecream/robot_state', 10)
        self.pub_grab     = self.create_publisher(String, '/icecream/cmd/grab_cup', 10)
        self.pub_dispense = self.create_publisher(String, '/icecream/cmd/dispense_icecream', 10)
        self.pub_serve    = self.create_publisher(String, '/icecream/cmd/serve', 10)

        self.create_subscription(String, '/icecream/selected_flavor', self._on_flavor_selected, 10)
        self.create_subscription(String, '/icecream/done/cup_grabbed',
            lambda msg: self._on_done('cup_grabbed', msg), 10)
        self.create_subscription(String, '/icecream/done/icecream_dispensed',
            lambda msg: self._on_done('icecream_dispensed', msg), 10)
        self.create_subscription(String, '/icecream/done/served',
            lambda msg: self._on_done('served', msg), 10)

        self._publish_state('idle')
        self.get_logger().info('✓ State machine ready. Waiting for flavor selection...')

    def _on_flavor_selected(self, msg: String):
        if self.busy:
            self.get_logger().warn(f'Already serving — ignoring new request.')
            return
        self.active_flavor = msg.data
        self.get_logger().info(f'▶ Flavor selected: {self.active_flavor}')
        threading.Thread(target=self._run_sequence, daemon=True).start()

    def _on_done(self, signal: str, msg: String):
        if signal == self._expected_done:
            self.get_logger().info(f'  ✓ Hardware confirmed: {signal}')
            self._done_event.set()

    def _run_sequence(self):
        self.busy = True
        try:
            self._transition('grabbing_cup')
            self._command_and_wait(self.pub_grab, self.active_flavor,
                                   'cup_grabbed', 10.0, 'grab cup')

            self._transition('getting_icecream')
            self._command_and_wait(self.pub_dispense, self.active_flavor,
                                   'icecream_dispensed', 15.0, 'dispense ice cream')

            self._transition('serving')
            self._command_and_wait(self.pub_serve, self.active_flavor,
                                   'served', 30.0, 'serve')

            # ── Done — hold for 4 seconds so dashboard can animate ────────────
            self._transition('done')
            self.get_logger().info(f'✦ Order complete: {self.active_flavor} — waiting 4s...')
            time.sleep(4.0)
            self.get_logger().info('  Returning to idle.')

        except TimeoutError as e:
            self.get_logger().error(f'Timeout: {e}')
        finally:
            self.active_flavor = ''
            self.busy = False
            self._transition('idle')
            self.get_logger().info('◉ Ready for next order.')

    def _transition(self, new_state: str):
        self.current_state = new_state
        self._publish_state(new_state)
        self.get_logger().info(f'  → State: {new_state}')

    def _publish_state(self, state: str):
        msg = String()
        msg.data = state
        self.pub_state.publish(msg)

    def _command_and_wait(self, publisher, payload, expected_done, timeout, step):
        self._done_event.clear()
        self._expected_done = expected_done
        cmd = String()
        cmd.data = payload
        publisher.publish(cmd)
        self.get_logger().info(f'  → Commanded: {step}')
        if not self._done_event.wait(timeout=timeout):
            raise TimeoutError(f'Timed out waiting for "{expected_done}"')
        self._expected_done = None


def main(args=None):
    rclpy.init(args=args)
    node = IceCreamStateMachine()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
