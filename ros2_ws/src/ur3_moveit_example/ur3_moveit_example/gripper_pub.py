import rclpy
import time

from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class GripperPublisher(Node):
    def __init__(self):
        super().__init__('gripper_publisher')
        
        self.publisher_ = self.create_publisher(
            Float64MultiArray, 
            '/gripper_controller/commands', 
            10
        )
        
    def gripper_open(self):
        msg = Float64MultiArray()
        msg.data = [0.0]  # Open position
        self.publisher_.publish(msg)
        self.get_logger().info('Opening gripper')
        
    def gripper_close(self):
        msg = Float64MultiArray()
        msg.data = [0.4]  # Closed position
        self.publisher_.publish(msg)
        self.get_logger().info('Closing gripper')
        
def main(args=None):
    rclpy.init(args=args)
    
    gripper_publisher = GripperPublisher()
    
    # Wait for subscriber/controller to connect
    while gripper_publisher.publisher_.get_subscription_count() == 0:
        gripper_publisher.get_logger().info(
            "Waiting for gripper subscriber..."
        )
        rclpy.spin_once(gripper_publisher, timeout_sec=0.5)
        
    # Example usage: close and openthe gripper
    gripper_publisher.gripper_close()
    rclpy.spin_once(gripper_publisher, timeout_sec=5)  # Allow time for the message to be sent
    
    gripper_publisher.gripper_open()
    rclpy.spin_once(gripper_publisher, timeout_sec=5)  # Allow time for the message to be sent
    
    gripper_publisher.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()