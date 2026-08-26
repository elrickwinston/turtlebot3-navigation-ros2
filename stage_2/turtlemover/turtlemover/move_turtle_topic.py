import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Int32
import math

class MoveTurtleTopic(Node):

    def __init__(self):
        super().__init__('move_turtle_topic')

        # Publisher to move the turtle
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Subscriber to receive how many circles to drive
        self.subscription = self.create_subscription(
            Int32,
            'move_turtle_circles',
            self.circles_callback,
            10)

        # Subscriber to track turtle position
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)

        # State variables
        self.target_circles = 0
        self.circles_done = 0
        self.moving = False
        self.starting_x = None
        self.starting_y = None
        self.started = False

    def circles_callback(self, msg):
        self.get_logger().info(f'Received: drive {msg.data} circles')
        self.target_circles = msg.data
        self.circles_done = 0
        self.moving = True
        self.starting_x = None  # reset starting position
        self.started = False

    def pose_callback(self, msg):
        if not self.moving:
            return

        # Save starting position
        if self.starting_x is None:
            self.starting_x = msg.x
            self.starting_y = msg.y
            self.started = False
            # Start moving
            self.timer = self.create_timer(0.5, self.move_callback)
            return

        distance = math.sqrt(
            (msg.x - self.starting_x) ** 2 +
            (msg.y - self.starting_y) ** 2)

        if self.started and distance < 0.5:
            self.circles_done += 1
            self.get_logger().info(f'Circles completed: {self.circles_done}/{self.target_circles}')
            self.starting_x = msg.x
            self.starting_y = msg.y
            self.started = False

            if self.circles_done >= self.target_circles:
                self.get_logger().info('Done! Stopping turtle.')
                self.moving = False
                self.timer.cancel()
                stop_msg = Twist()
                self.publisher_.publish(stop_msg)

        if distance > 1.0:
            self.started = True

    def move_callback(self):
        if self.moving:
            msg = Twist()
            msg.linear.x = 2.0
            msg.angular.z = 1.0
            self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    move_turtle_topic = MoveTurtleTopic()
    rclpy.spin(move_turtle_topic)
    move_turtle_topic.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
