import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class CvColorDetect(Node):

    def __init__(self):
        super().__init__('cv_color_detect')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10)
        self.br = CvBridge()
        self.get_logger().info('CvColorDetect node started!')

    def listener_callback(self, data):
        img = self.br.imgmsg_to_cv2(data, 'bgr8')
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # White line detection
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Yellow line detection
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Show all windows
        cv2.imshow('original', img)
        cv2.imshow('white line', white_mask)
        cv2.imshow('yellow line', yellow_mask)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = CvColorDetect()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
