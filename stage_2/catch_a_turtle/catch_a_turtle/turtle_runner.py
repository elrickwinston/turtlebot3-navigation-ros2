import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleRunner(Node):

    def __init__(self):
        super().__init__('turtle_runner')

        # Publisher to move turtle1 in circles
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.move_callback)

    def move_callback(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    turtle_runner = TurtleRunner()
    rclpy.spin(turtle_runner)
    turtle_runner.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
