import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import math

class AvoidObstacle(Node):
    # State Machine
    TRACK_WHITE = 0
    TRACK_YELLOW = 1
    MERGE_LEFT = 2
    MERGE_RIGHT = 3

    def __init__(self):
        super().__init__('avoid_obstacle')
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.br = CvBridge()
        
        self.state = self.TRACK_WHITE
        self.ranges = []
        self.merge_start_time = self.get_clock().now()
        
        # Merge Settings
        self.merge_duration = 1.8 # Seconds to blindly swerve away from the box
        
        self.get_logger().info('AvoidObstacle node started! (Forced Blind-Merge Active)')

    def scan_callback(self, msg):
        self.ranges = msg.ranges

    def get_front_distance(self):
        if not self.ranges:
            return 10.0
        # 30-degree front cone to ensure we only react to things directly in front
        front_rays = self.ranges[0:15] + self.ranges[345:359]
        valid_front = [r for r in front_rays if not math.isinf(r) and r > 0.15]
        return min(valid_front) if valid_front else 10.0

    def image_callback(self, data):
        img = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')
        img = cv2.resize(img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Stricter masks to prevent the red box from confusing the line trackers
        mask_white = cv2.inRange(imgHSV, np.array([0, 0, 180]), np.array([180, 40, 255]))
        mask_yellow = cv2.inRange(imgHSV, np.array([25, 100, 100]), np.array([35, 255, 255]))

        h, w = mask_white.shape
        mask_white[0:int(h * 0.4), :] = 0 
        mask_yellow[0:int(h * 0.4), :] = 0 

        M_w = cv2.moments(mask_white)
        M_y = cv2.moments(mask_yellow)

        white_detected = M_w['m00'] > 50
        yellow_detected = M_y['m00'] > 50

        cx_white = int(M_w['m10'] / M_w['m00']) if white_detected else w // 2
        cx_yellow = int(M_y['m10'] / M_y['m00']) if yellow_detected else w // 2

        twist = Twist()
        front_dist = self.get_front_distance()
        current_time = self.get_clock().now()

        # ---------------- STATE MACHINE ----------------

        # 1. Trigger the Evasion Maneuver
        if front_dist < 0.75:
            if self.state == self.TRACK_WHITE:
                self.get_logger().info('Obstacle Detected! Executing Hard Merge LEFT.')
                self.state = self.MERGE_LEFT
                self.merge_start_time = current_time
            elif self.state == self.TRACK_YELLOW:
                self.get_logger().info('Obstacle Detected! Executing Hard Merge RIGHT.')
                self.state = self.MERGE_RIGHT
                self.merge_start_time = current_time

        # 2. Execute Behaviors based on current State
        if self.state == self.MERGE_LEFT:
            # Swerve left away from obstacle (ignore camera)
            twist.linear.x = 0.1
            twist.angular.z = 0.35 
            if (current_time - self.merge_start_time).nanoseconds / 1e9 > self.merge_duration:
                self.get_logger().info('Merge Complete. Locking onto YELLOW lane.')
                self.state = self.TRACK_YELLOW

        elif self.state == self.MERGE_RIGHT:
            # Swerve right away from obstacle (ignore camera)
            twist.linear.x = 0.1
            twist.angular.z = -0.35
            if (current_time - self.merge_start_time).nanoseconds / 1e9 > self.merge_duration:
                self.get_logger().info('Merge Complete. Locking onto WHITE lane.')
                self.state = self.TRACK_WHITE

        elif self.state == self.TRACK_WHITE:
            # Normal PID Tracking White
            if white_detected:
                error = (w // 2) - cx_white
                twist.linear.x = 0.1
                twist.angular.z = float(np.clip(0.01 * error, -0.3, 0.3))
            else:
                twist.linear.x = 0.05
                twist.angular.z = -0.2 # Hunt right if lost

        elif self.state == self.TRACK_YELLOW:
            # Normal PID Tracking Yellow
            if yellow_detected:
                error = (w // 2) - cx_yellow
                twist.linear.x = 0.1
                twist.angular.z = float(np.clip(0.01 * error, -0.3, 0.3))
            else:
                twist.linear.x = 0.05
                twist.angular.z = 0.2 # Hunt left if lost

        self.cmd_pub.publish(twist)
        
        # Draw targeting dots for debugging
        if self.state == self.TRACK_WHITE and white_detected:
            cv2.circle(img, (cx_white, int(M_w['m01'] / M_w['m00'])), 6, (255, 255, 255), -1)
        elif self.state == self.TRACK_YELLOW and yellow_detected:
            cv2.circle(img, (cx_yellow, int(M_y['m01'] / M_y['m00'])), 6, (0, 255, 255), -1)

        cv2.imshow('camera', img)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = AvoidObstacle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
