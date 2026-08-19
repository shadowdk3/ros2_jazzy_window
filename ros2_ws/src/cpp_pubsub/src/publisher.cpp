#include <memory>

#include "rclcpp/rclcpp.hpp"            // ROS 2 C++ client library
#include "std_msgs/msg/string.hpp"      // Standard ROS 2 String message

// Create a class for our publisher node
class PublisherNode : public rclcpp::Node
{
    public:

        // Constructor
        PublisherNode() : Node("publisher_node")
        {
            // Create a publisher
            //
            // Message type: std_msgs::msg::String
            // Topic name: "chatter"
            // Queue size: 10
            publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);


            // Create a timer
            //
            // The callback function will run every 1 second.
            // When the timer triggers, it calls publish_message().
            timer_ = this->create_wall_timer(
                std::chrono::seconds(1),
                std::bind(&PublisherNode::publish_message, this));
        }


    private:
        int _count = 0;                                                         // Counter for number of publisher message

        // This function is called every 1 second
        void publish_message()
        {
            auto message = std_msgs::msg::String();                             // Create a String message
            message.data = "no. of publish - " + std::to_string(_count);        // Set the message content

            publisher_->publish(message);                                       // Publish the message to /chatter

            RCLCPP_INFO(                                                        // Print the message to the terminal
                this->get_logger(),
                "Publishing: %s",
                message.data.c_str()
            );

            _count++;                                                           // Increase Counter
        }

        // Publisher object
        //
        // It is used to publish messages to /chatter.
        rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;


        // Timer object
        //
        // It triggers publish_message() every 1 second.
        rclcpp::TimerBase::SharedPtr timer_;
};

// Program entry point
int main(int argc, char * argv[])
{
    // Initialize ROS 2
    rclcpp::init(argc, argv);


    // Create the PublisherNode
    //
    // spin() keeps the node running
    // and allows callbacks (such as the timer) to execute.
    rclcpp::spin(
        std::make_shared<PublisherNode>()
    );


    // Shutdown ROS 2
    rclcpp::shutdown();

    return 0;
}