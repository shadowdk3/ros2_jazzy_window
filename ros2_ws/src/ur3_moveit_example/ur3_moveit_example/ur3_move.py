#!/usr/bin/env python3
# Copyright (c) 2024 FZI Forschungszentrum Informatik
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the {copyright_holder} nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

#
# Author: Felix Exner

# This is an example of how to interface the robot without any additional ROS components. For
# real-life applications, we do recommend to use something like MoveIt!

import time
import sys

import rclpy                                                            # ROS 2 Python client library.
from rclpy.action import ActionClient           

from builtin_interfaces.msg import Duration                             # ROS 2 message types used to describe trajectory timing
from action_msgs.msg import GoalStatus                                  # Used to check the result/status of the ROS 2 action
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint   # Messages used to describe a joint trajectory
from control_msgs.action import FollowJointTrajectory                   # Action definition used by the Joint Trajectory Controller (JTC)
from control_msgs.msg import JointTolerance                             # Used to specify acceptable position/velocity errors for each joint

# ---------------------------------------------------------------------------
# TRAJECTORY DEFINITIONS
# ---------------------------------------------------------------------------
#
# Each trajectory contains a list of trajectory points.
#
# A trajectory point contains:
#   - positions: desired joint positions in radians
#   - velocities: desired joint velocities
#   - time_from_start: when the robot should reach this point
#
# There are six joints because this example is intended for a 6-DOF robot
#
# The robot will execute traj0 first and traj1 second

TRAJECTORIES = {
    "traj0": [
        {
            "positions": [0.043128, -1.28824, 1.37179, -1.82208, -1.63632, -0.18],
            "velocities": [0, 0, 0, 0, 0, 0],
            "time_from_start": Duration(sec=4, nanosec=0),
        },
        {
            "positions": [-0.195016, -1.70093, 0.902027, -0.944217, -1.52982, -0.195171],
            "velocities": [0, 0, 0, 0, 0, 0],
            "time_from_start": Duration(sec=8, nanosec=0),
        },
    ],
    "traj1": [
        {
            "positions": [-0.195016, -1.70094, 0.902027, -0.944217, -1.52982, -0.195171],
            "velocities": [0, 0, 0, 0, 0, 0],
            "time_from_start": Duration(sec=0, nanosec=0),
        },
        {
            "positions": [0.30493, -0.982258, 0.955637, -1.48215, -1.72737, 0.204445],
            "velocities": [0, 0, 0, 0, 0, 0],
            "time_from_start": Duration(sec=8, nanosec=0),
        },
    ],
}


class JTCClient(rclpy.node.Node):
    """Small test client for the jtc."""

    def __init__(self):
        super().__init__("jtc_client")
         # -------------------------------------------------------------------
        # ROS PARAMETERS
        # -------------------------------------------------------------------
        #
        # The controller name can be changed when launching the node
        # The default controller is the scaled joint trajectory controller
        
        self.declare_parameter("controller_name", "scaled_joint_trajectory_controller")
        
        # Optional prefix that can be added to every joint name
        # This is useful when using namespaces or multiple robot instances
        self.declare_parameter("tf_prefix", "")
        
        # List of robot joint names
        #
        # These names must match the joint names expected by the controller
        self.declare_parameter(
            "joints",
            [
                "shoulder_pan_joint",
                "shoulder_lift_joint",
                "elbow_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint",
            ],
        )

        # The FollowJointTrajectory action is exposed by the controller
        # under the "/follow_joint_trajectory" action name
        controller_name = self.get_parameter("controller_name").value + "/follow_joint_trajectory"
        
        # Read the configured TF prefix
        self.tf_prefix = self.get_parameter("tf_prefix").value
        
        # Add the TF prefix to every joint name
        self.joints = [
            self.tf_prefix + joint_name for joint_name in self.get_parameter("joints").value
        ]

        # Make sure that at least one joint was configured
        if self.joints is None or len(self.joints) == 0:
            raise Exception('"joints" parameter is required')

        # -------------------------------------------------------------------
        # ACTION CLIENT
        # -------------------------------------------------------------------
        #
        # Create an action client for the FollowJointTrajectory action
        #
        # An action client allows this node to:
        #   1. Send a trajectory goal
        #   2. Receive confirmation that the goal was accepted
        #   3. Wait for the robot to finish
        #   4. Receive the final execution result
        
        self._action_client = ActionClient(self, FollowJointTrajectory, controller_name)
        self.get_logger().info(f"Waiting for action server on {controller_name}")
        
        # Block until the controller's action server becomes available.
        self._action_client.wait_for_server()

        # Convert the dictionary-based trajectory definitions above into
        # proper ROS 2 JointTrajectory messages
        self.parse_trajectories()
        
        # Index used to keep track of which trajectory should execute next
        self.i = 0
        
        # Futures are used to asynchronously track action requests/results
        self._send_goal_future = None
        self._get_result_future = None
        
        # Start executing the first trajectory.
        self.execute_next_trajectory()

    def parse_trajectories(self):
        
        # Dictionary that will contain ROS JointTrajectory messages
        self.goals = {}

        # Process every trajectory defined in TRAJECTORIES.
        for traj_name in TRAJECTORIES:
            goal = JointTrajectory()                            # Create a JointTrajectory message
            goal.joint_names = self.joints                      # Tell the controller which joints the trajectory controls
            for pt in TRAJECTORIES[traj_name]:                  # Convert each dictionary point into a ROS message
                point = JointTrajectoryPoint()                  # Create a ROS trajectory point
                point.positions = pt["positions"]               # Set the desired joint positions
                point.velocities = pt["velocities"]             # Set the desired joint velocities
                point.time_from_start = pt["time_from_start"]   # Set when this point should be reached
                goal.points.append(point)                       # Add the point to the trajectory

            self.goals[traj_name] = goal                        # Store the completed ROS trajectory

    def execute_next_trajectory(self):
        """Execute the next trajectory in the sequence."""

        # If all trajectories have already been executed, stop the node
        if self.i >= len(self.goals):
            self.get_logger().info("Done with all trajectories")
            raise SystemExit
        
        traj_name = list(self.goals)[self.i]                    # Get the trajectory name using the current index
        self.i = self.i + 1                                     # Increment the index so the next call executes the next trajectory
        if traj_name:                                           # Execute the selected trajectory
            self.execute_trajectory(traj_name)

    def execute_trajectory(self, traj_name):
        """Send a trajectory to the Joint Trajectory Controller."""
         
        self.get_logger().info(f"Executing trajectory {traj_name}")
        goal = FollowJointTrajectory.Goal()                     # Create a FollowJointTrajectory action goal
        goal.trajectory = self.goals[traj_name]                 # Attach the JointTrajectory message created earlier

        # Allow the controller 0.5 seconds of additional time to reach
        # the final goal position.
        goal.goal_time_tolerance = Duration(sec=0, nanosec=500000000)
       
        # Define position and velocity tolerances for each joint.
        #
        # A trajectory is considered successful if the robot reaches
        # the target within these tolerances.
        goal.goal_tolerance = [
            JointTolerance(position=0.01, velocity=0.01, name=self.joints[i]) for i in range(6)
        ]

        # Send the goal asynchronously.
        #
        # This does not block the ROS node while the robot is moving.
        self._send_goal_future = self._action_client.send_goal_async(goal)
        
        # When the controller responds, call goal_response_callback().
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle the controller's response to a trajectory goal."""
                
        goal_handle = future.result()                           # Get the action goal handle returned by the controller
        if not goal_handle.accepted:                            # Check whether the controller accepted the trajectory
            self.get_logger().error("Goal rejected :(")
            raise RuntimeError("Goal rejected :(")

        self.get_logger().debug("Goal accepted :)")

        # Request the final result of the trajectory execution.
        #
        # This is asynchronous, so the ROS node can continue processing
        # other events while the robot moves.
        self._get_result_future = goal_handle.get_result_async()
        
        # When the trajectory finishes, call get_result_callback().
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handle the result returned after trajectory execution."""

        result = future.result().result                                                     # Extract the FollowJointTrajectory result
        status = future.result().status                                                     # Extract the ROS 2 action status
        self.get_logger().info(f"Done with result: {self.status_to_str(status)}")           # Print a human-readable status message
        
        # Check whether the trajectory completed successfully
        if status == GoalStatus.STATUS_SUCCEEDED:
            time.sleep(2)                                                                   # Wait two seconds before starting the next trajectory
            self.execute_next_trajectory()                                                  # Start the next trajectory.
        else:
            # If the controller returned an error code, print a readable
            # description of the error.
            if result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
                self.get_logger().error(
                    f"Done with result: {self.error_code_to_str(result.error_code)}"
                )
            # Stop execution because the trajectory failed
            raise RuntimeError("Executing trajectory failed. " + result.error_string)

    @staticmethod
    def error_code_to_str(error_code):
        if error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            return "SUCCESSFUL"
        if error_code == FollowJointTrajectory.Result.INVALID_GOAL:
            return "INVALID_GOAL"
        if error_code == FollowJointTrajectory.Result.INVALID_JOINTS:
            return "INVALID_JOINTS"
        if error_code == FollowJointTrajectory.Result.OLD_HEADER_TIMESTAMP:
            return "OLD_HEADER_TIMESTAMP"
        if error_code == FollowJointTrajectory.Result.PATH_TOLERANCE_VIOLATED:
            return "PATH_TOLERANCE_VIOLATED"
        if error_code == FollowJointTrajectory.Result.GOAL_TOLERANCE_VIOLATED:
            return "GOAL_TOLERANCE_VIOLATED"

    @staticmethod
    def status_to_str(error_code):
        if error_code == GoalStatus.STATUS_UNKNOWN:
            return "UNKNOWN"
        if error_code == GoalStatus.STATUS_ACCEPTED:
            return "ACCEPTED"
        if error_code == GoalStatus.STATUS_EXECUTING:
            return "EXECUTING"
        if error_code == GoalStatus.STATUS_CANCELING:
            return "CANCELING"
        if error_code == GoalStatus.STATUS_SUCCEEDED:
            return "SUCCEEDED"
        if error_code == GoalStatus.STATUS_CANCELED:
            return "CANCELED"
        if error_code == GoalStatus.STATUS_ABORTED:
            return "ABORTED"


def main(args=None):
    rclpy.init(args=args)               # init ROS2

    exit_code = 0

    jtc_client = JTCClient()
    try:
        rclpy.spin(jtc_client)
    except RuntimeError as err:
        jtc_client.get_logger().error(str(err))
        exit_code = 1
    except SystemExit:
        rclpy.logging.get_logger("jtc_client").info("Done")

    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()