#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint

from control_msgs.action import GripperCommand


class RobotGripperMove(Node):

    def __init__(self):
        super().__init__("robot_gripper_move")

        # --------------------------------------------------
        # MoveIt arm
        # --------------------------------------------------

        self.move_client = ActionClient(
            self,
            MoveGroup,
            "/move_action"
        )

        # --------------------------------------------------
        # Gripper
        # --------------------------------------------------

        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            "/gripper_controller/gripper_cmd"
        )

    # ======================================================
    # ARM
    # ======================================================

    def move_arm(self, positions):

        self.get_logger().info("Waiting for MoveIt...")

        if not self.move_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                "MoveIt /move_action not available"
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

        constraints = Constraints()

        for name, position in zip(joint_names, positions):

            constraint = JointConstraint()

            constraint.joint_name = name
            constraint.position = position
            constraint.tolerance_above = 0.01
            constraint.tolerance_below = 0.01
            constraint.weight = 1.0

            constraints.joint_constraints.append(
                constraint
            )

        # --------------------------------------------------
        # MoveIt goal
        # --------------------------------------------------

        goal = MoveGroup.Goal()

        goal.request.group_name = "arm"

        goal.request.goal_constraints.append(
            constraints
        )

        goal.request.allowed_planning_time = 5.0
        goal.request.num_planning_attempts = 10

        goal.request.pipeline_id = "ompl"
        goal.request.planner_id = "RRTConnectkConfigDefault"

        # Slow initial testing
        goal.request.max_velocity_scaling_factor = 0.2
        goal.request.max_acceleration_scaling_factor = 0.2

        self.get_logger().info(
            f"Planning arm to {positions}"
        )

        future = self.move_client.send_goal_async(goal)

        rclpy.spin_until_future_complete(
            self,
            future
        )

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                "MoveIt rejected the arm goal"
            )

            return False

        self.get_logger().info(
            "MoveIt accepted arm goal"
        )

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result().result

        error_code = result.error_code.val

        self.get_logger().info(
            f"MoveIt result code: {error_code}"
        )

        if error_code == 1:

            self.get_logger().info(
                "Arm movement complete"
            )

            return True

        self.get_logger().error(
            f"Arm movement failed: {error_code}"
        )

        return False

    # ======================================================
    # GRIPPER
    # ======================================================

    def move_gripper(self, position):

        self.get_logger().info(
            "Waiting for gripper controller..."
        )

        if not self.gripper_client.wait_for_server(
            timeout_sec=10.0
        ):

            self.get_logger().error(
                "Gripper action server not available"
            )

            return False

        goal = GripperCommand.Goal()

        goal.command.position = position

        # 0.0 = open
        # 0.8 = closed
        goal.command.max_effort = 0.0

        self.get_logger().info(
            f"Moving gripper to {position}"
        )

        future = self.gripper_client.send_goal_async(
            goal
        )

        rclpy.spin_until_future_complete(
            self,
            future
        )

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                "Gripper goal rejected"
            )

            return False

        self.get_logger().info(
            "Gripper goal accepted"
        )

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result().result

        self.get_logger().info(
            f"Gripper reached position: {result.position}"
        )

        return True


def main(args=None):

    rclpy.init(args=args)

    node = RobotGripperMove()

    # ======================================================
    # 1. OPEN GRIPPER
    # ======================================================

    node.move_gripper(0.0)

    # ======================================================
    # 2. MOVE ARM HOME
    # ======================================================

    node.move_arm([
        0.0,       # shoulder_pan_joint
        -1.7009,   # shoulder_lift_joint
        0.0,       # elbow_joint
        0.0,       # wrist_1_joint
        0.0,       # wrist_2_joint
        0.0,       # wrist_3_joint
    ])

    # ======================================================
    # 3. MOVE ARM TO TARGET
    # ======================================================

    node.move_arm([
        0.0,
        -1.0,
        1.0,
        -1.5,
        -1.5,
        0.0,
    ])

    # ======================================================
    # 4. CLOSE GRIPPER
    # ======================================================

    node.move_gripper(0.8)

    # ======================================================
    # 5. MOVE ARM HOME
    # ======================================================

    node.move_arm([
        0.0,
        -1.7009,
        0.0,
        0.0,
        0.0,
        0.0,
    ])

    # ======================================================
    # 6. OPEN GRIPPER
    # ======================================================

    node.move_gripper(0.0)

    node.get_logger().info(
        "Sequence complete!"
    )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()