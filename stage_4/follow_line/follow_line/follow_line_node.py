import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np


class LineFollower(Node):

    def __init__(self):
        super().__init__('follow_line_node')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10)
        self.scan_subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.br = CvBridge()
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.linear_velocity_gain = 0.05
        self.angular_velocity_gain = 0.012
        self.last_angular = 0.0
        self.obstacle_detected = False
        self.get_logger().info('LineFollower node started!')

    def scan_callback(self, msg):
        # Check front distance (same as drive_to_wall)
        front_dist = min(msg.ranges[0], msg.ranges[5], msg.ranges[355])
        if front_dist < 0.5:
            self.obstacle_detected = True
            self.get_logger().info(f'Obstacle detected! Distance: {front_dist:.2f}')
        else:
            self.obstacle_detected = False

    def listener_callback(self, data):
        img = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')
        img = cv2.resize(img, None, fx=0.25, fy=0.25,
                         interpolation=cv2.INTER_CUBIC)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # White line detection
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 50, 255])
        mask = cv2.inRange(imgHSV, lower_white, upper_white)

# Single bottom row — find white pixel CLOSEST to center
        row_index = mask.shape[0] - 2
        pixel_row = mask[row_index, :]
        img_center_x = mask.shape[1] // 2

        white_pixels = np.where(pixel_row > 0)[0]

        twist = Twist()

        if len(white_pixels) > 0:
            # Pick white pixel closest to center
            closest = white_pixels[np.argmin(np.abs(white_pixels - img_center_x))]
            error = img_center_x - closest

            angular_velocity = self.angular_velocity_gain * error
            angular_velocity = np.clip(angular_velocity, -0.8, 0.8)

            twist.linear.x = self.linear_velocity_gain
            twist.angular.z = float(angular_velocity)

            cv2.circle(img, (closest, row_index), 8, (0, 255, 0), -1)
            self.get_logger().info(
                f'Closest white: {closest} | Error: {error} | Angular: {angular_velocity:.3f}')
            self.last_angular = float(angular_velocity)
        else:
            self.get_logger().info('Line lost! Continuing last turn...')
            twist.linear.x = 0.05
            twist.angular.z = self.last_angular * 3

        self.publisher_.publish(twist)
        cv2.imshow('mask', mask)
        cv2.imshow('camera', img)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    line_follower = LineFollower()
    rclpy.spin(line_follower)
    line_follower.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
