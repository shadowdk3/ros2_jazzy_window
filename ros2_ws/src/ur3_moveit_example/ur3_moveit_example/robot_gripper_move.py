#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint
from shape_msgs.msg import SolidPrimitive

"""
ros2 launch robot_gripper_moveit_setup demo.launch.py
ros2 run ur3_moveit_example robot_gripper_move
"""

class SimpleMove(Node):

    def __init__(self):
        super().__init__("simple_move")

        self.client = ActionClient(
            self,
            MoveGroup,
            "/move_action"
        )

    def move_arm(self, positions):

        self.get_logger().info("Waiting for MoveIt...")

        if not self.client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                "MoveIt action server /move_action not available"
            )
            return False

        joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        # --------------------------------------------------
        # Joint constraints
        # --------------------------------------------------

        constraints = Constraints()

        for name, position in zip(joint_names, positions):

            constraint = JointConstraint()

            constraint.joint_name = name
            constraint.position = position
            constraint.tolerance_above = 0.01
            constraint.tolerance_below = 0.01
            constraint.weight = 1.0

            constraints.joint_constraints.append(constraint)

        # --------------------------------------------------
        # MoveGroup goal
        # --------------------------------------------------

        goal = MoveGroup.Goal()

        goal.request.group_name = "arm"

        goal.request.goal_constraints.append(constraints)

        # Planning configuration
        goal.request.allowed_planning_time = 5.0
        goal.request.num_planning_attempts = 10

        # Use OMPL
        goal.request.pipeline_id = "ompl"

        # Planner
        goal.request.planner_id = "RRTConnectkConfigDefault"

        # Slow/safe initial test
        goal.request.max_velocity_scaling_factor = 0.2
        goal.request.max_acceleration_scaling_factor = 0.2

        # --------------------------------------------------
        # Send goal
        # --------------------------------------------------

        self.get_logger().info(
            f"Planning to: {positions}"
        )

        future = self.client.send_goal_async(goal)

        rclpy.spin_until_future_complete(
            self,
            future
        )

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                "MoveIt rejected the goal"
            )

            return False

        self.get_logger().info(
            "MoveIt accepted the goal"
        )

        # --------------------------------------------------
        # Wait for result
        # --------------------------------------------------

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result().result

        error_code = result.error_code.val

        self.get_logger().info(
            f"MoveIt error code: {error_code}"
        )

        if error_code == 1:

            self.get_logger().info(
                "Motion completed successfully!"
            )

            return True

        self.get_logger().error(
            f"MoveIt failed with error code {error_code}"
        )

        return False


def main(args=None):

    rclpy.init(args=args)

    node = SimpleMove()

    # --------------------------------------------------
    # Target joint positions
    # --------------------------------------------------
    #
    # shoulder_pan
    # shoulder_lift
    # elbow
    # wrist_1
    # wrist_2
    # wrist_3
    #
    # radians
    #

    target = [
        0.0,
        -1.0,
        1.0,
        -1.5,
        -1.5,
        0.0,
    ]

    success = node.move_arm(target)

    node.destroy_node()

    rclpy.shutdown()

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()