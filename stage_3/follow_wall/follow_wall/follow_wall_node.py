import math
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class FollowWall(Node):
    def __init__(self):
        super().__init__("FollowWall")
        self.publisher_name = self.create_publisher(Twist, "/cmd_vel", 10)
        self.subscriber_name = self.create_subscription(LaserScan, "/scan", self.scan_callback, 10)
        self.state = "FORWARD"
        self.wait_start_time = None
        self.target_distance = 0.5

    def scan_callback(self, msg):
        ranges = msg.ranges
        cmd = Twist()
        front = min(ranges[0], ranges[5], ranges[355])
        r260 = ranges[260]
        r280 = ranges[280]
        if math.isinf(front): front = 10.0
        if math.isinf(r260): r260 = 10.0
        if math.isinf(r280): r280 = 10.0
        self.get_logger().info(f"State: {self.state} | Front: {front:.2f} | R260: {r260:.2f} | R280: {r280:.2f}")

        if self.state == "FORWARD":
            if front > 0.85:
                cmd.linear.x = 0.25
                cmd.angular.z = 0.0
            elif front > 0.60:
                cmd.linear.x = 0.10
                cmd.angular.z = 0.0
            elif front > 0.55:
                cmd.linear.x = 0.05
                cmd.angular.z = 0.0
            else:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.state = "TURNING"

        elif self.state == "TURNING":
            parallel_diff = abs(r260 - r280)
            avg_right = (r260 + r280) / 2.0
            aligned = (front > 1.2 and avg_right < 0.8 and parallel_diff < 0.04)
            if aligned:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.state = "WAIT"
                self.wait_start_time = self.get_clock().now()
            else:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.3

        elif self.state == "WAIT":
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            elapsed = (self.get_clock().now() - self.wait_start_time).nanoseconds / 1e9
            if elapsed >= 2.5:
                self.state = "FOLLOW"

        elif self.state == "FOLLOW":
            avg_right = (r260 + r280) / 2.0
            parallel_error = r280 - r260
            if front < 0.55:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.state = "TURNING"
            elif avg_right > 0.70:
                cmd.linear.x = 0.08
                cmd.angular.z = -0.35
            elif avg_right < 0.40:
                cmd.linear.x = 0.08
                cmd.angular.z = 0.35
            else:
                cmd.linear.x = 0.15
                cmd.angular.z = -2.0 * parallel_error

        self.publisher_name.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    follow_wall_node = FollowWall()
    rclpy.spin(follow_wall_node)
    follow_wall_node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
