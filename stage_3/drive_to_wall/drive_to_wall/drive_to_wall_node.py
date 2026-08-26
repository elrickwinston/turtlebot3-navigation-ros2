import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class DriveToWallNode(Node):

    def __init__(self):
        super().__init__('drive_to_wall_node')

        # Publisher to drive the turtlebot in linear x direction
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscriber to read scan data
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        # Timer to publish movement
        self.timer = self.create_timer(0.1, self.move_callback)

        # Store latest scan data
        self.scan_data = None

        self.get_logger().info('DriveToWallNode started!')

    def scan_callback(self, msg):
        # Store the scan data
        self.scan_data = msg

    def move_callback(self):
        msg = Twist()

        # Check if scan data is available
        if self.scan_data is not None:
            # Get the [0] element of ranges
            front_distance = self.scan_data.ranges[0]
            self.get_logger().info(f'Front distance: {front_distance}')

            # Stop if closer than 1 meter to wall
            if front_distance < 1.0:
                self.get_logger().info('Wall detected! Stopping.')
                msg.linear.x = 0.0
            else:
                # Drive forward with speed 0.5
                msg.linear.x = 0.5

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    drive_to_wall_node = DriveToWallNode()
    rclpy.spin(drive_to_wall_node)
    drive_to_wall_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
