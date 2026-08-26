import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import random


class GoalPub(Node):

    def __init__(self):
        super().__init__('goal_pub')

        # Publisher to /goal_pose
        self.publisher_ = self.create_publisher(PoseStamped, '/goal_pose', 10)

        # Timer to publish goal every 15 seconds
        self.timer = self.create_timer(15.0, self.publish_goal)

        self.get_logger().info('GoalPub node started! Publishing random goals...')

    def publish_goal(self):
        msg = PoseStamped()

        # Set frame
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()

        # Random position within the map bounds
        msg.pose.position.x = random.uniform(-1.5, 1.5)
        msg.pose.position.y = random.uniform(-1.5, 1.5)
        msg.pose.position.z = 0.0

        # Default orientation (facing forward)
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = 0.0
        msg.pose.orientation.w = 1.0

        self.publisher_.publish(msg)
        self.get_logger().info(f'Published goal: x={msg.pose.position.x:.2f}, y={msg.pose.position.y:.2f}')


def main(args=None):
    rclpy.init(args=args)
    goal_pub = GoalPub()
    rclpy.spin(goal_pub)
    goal_pub.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
