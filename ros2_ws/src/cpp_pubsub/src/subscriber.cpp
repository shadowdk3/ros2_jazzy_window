#include <memory>

#include "rclcpp/rclcpp.hpp"                // ROS 2 C++ client library
#include "std_msgs/msg/string.hpp"          // ROS 2 String message type

// A ROS 2 node that subscribes to messages
class SubscriberNode : public rclcpp::Node
{
    public:
        // Constructor
        SubscriberNode(): Node("subscriber_node")  // Give the node the name "subscriber_node"
        {
            // Create a subscription to the "chatter" topic.
            //
            // std_msgs::msg::String:
            //   The type of message we expect.
            //
            // "chatter":
            //   The topic name.
            //
            // 10:
            //   QoS history depth. ROS 2 can keep up to 10 messages
            //   in the queue if they cannot be processed immediately.
            //
            // std::bind(...):
            //   Tell ROS 2 which function should be called
            //   whenever a message arrives.
            subscription_ = this->create_subscription<std_msgs::msg::String>(
                "chatter",
                10,
                std::bind(
                    &SubscriberNode::message_callback,
                    this,
                    std::placeholders::_1));
            
            RCLCPP_INFO(this->get_logger(), "Subscriber started");              // Print an informational message when the subscriber starts.
        }

    private:
        // This function is called whenever a message is received.
        //
        // message contains the received std_msgs/String message.
        void message_callback(const std_msgs::msg::String::SharedPtr message)
        {
            // Print the contents of the message.
            RCLCPP_INFO(
                this->get_logger(),
                "Received: '%s'",
                message->data.c_str());
        }

        // Stores the subscription object.
        //
        // As long as this object exists, the node remains subscribed
        // to the "chatter" topic.
        rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

// Program entry point
int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);                               // Initialize ROS 2.
    
    auto node = std::make_shared<SubscriberNode>();         // Create our SubscriberNode object.

    // Keep the node running and process incoming messages.
    //
    // When a message arrives, ROS 2 calls message_callback().
    rclcpp::spin(node);
    
    rclcpp::shutdown();                                     // Shut down ROS 2 when spin() finishes.

    return 0;
}