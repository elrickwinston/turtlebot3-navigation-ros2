import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class MoveTurtle(Node):

    def __init__(self):
        super().__init__('move_turtle')
        
        # Publisher to move the turtle
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Subscriber to track turtle position
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)
        
        # Timer to publish movement every 0.5 seconds
        self.timer = self.create_timer(0.5, self.move_callback)
        
        # Track circles
        self.starting_x = None
        self.starting_y = None
        self.circles = 0
        self.started = False

    def move_callback(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        self.publisher_.publish(msg)

    def pose_callback(self, msg):
        if self.starting_x is None:
            self.starting_x = msg.x
            self.starting_y = msg.y
            self.started = False
            return

        distance = math.sqrt(
            (msg.x - self.starting_x) ** 2 +
            (msg.y - self.starting_y) ** 2)

        if self.started and distance < 0.5:
            self.circles += 1
            self.get_logger().info(f'Circles completed: {self.circles}')
            self.started = False

        if distance > 1.0:
            self.started = True

def main(args=None):
    rclpy.init(args=args)
    move_turtle = MoveTurtle()
    rclpy.spin(move_turtle)
    move_turtle.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
