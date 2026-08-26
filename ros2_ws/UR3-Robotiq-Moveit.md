### UR3 + Robotiq + Moveit
---------------------------------

* ROS2 Jazzy
* WSL

## Prerequest

- Universal Robots Universal_Robots_ROS2_Description repository

```
git clone -b jazzy https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git
```

- robotiq repository

```
git clone -b kinetic-devel https://github.com/ros-industrial-attic/robotiq
```

## Combine UR3 and Robotiq

1. Create robot_gripper package for combine UR3 and Robotiq

```
ros2 pkg create robot_gripper --build-type ament_python --dependencies xacro ur_description
```

2. Create `urdf` and `meshes` folder under `robot_gripper` pacakge for store combine gripper and robot and gripper meshes

```
cd /Path/To/robot_gripper/
mkdir -p meshes urdf
```

3. Copy robotiq xacro and meshes into `urdf` and `meshes`

```
cp -r ~/PATHTO/robotiq_2f_85_gripper_visualization/urdf/* urdf/
cp -r ~/PATHTO/robotiq_2f_85_gripper_visualization/meshes/* meshes/
```

or 

copy
robotiq_2f_85_gripper.urdf.xacro
robotiq_2f_85_macro.urdf.xacro
2f_85.ros2_contol.xacro
to `urdf` folder

4. Create combine robot and gripper model, `robot_gripper.urdf.xacro`

  - include ur3 model
    
    ```
    <xacro:include filename="$(find ur_description)/urdf/ur_macro.xacro" />
    ```

  - include robotiq model

    ```
    <xacro:include filename="$(find robot_gripper)/urdf/robotiq_arg2f_85_model_macro.xacro" />
    ```

  - create a link for robot

    ```
    <link name="world"/>
    ```

  - define param for robot

    ```  
    <xacro:ur_robot
        ...
    </xacro:ur_robot>
    ```

  - define param for gripper
      
    ```
    <xacro:robotiq_arg2f_85 prefix=""/>
    ```

  - link robot and gripper, tool0 is the end joint of robot, and robotiq_arg2f_base_link is the base link of gripper 

    ```
    <joint name="gripper_to_robot" type="fixed">

      <parent link="tool0"/>
      <child link="robotiq_arg2f_base_link"/>

      <!-- Adjust this after looking at the model -->
      <origin
        xyz="0 0 0"
        rpy="0 0 0"/>
      
    </joint>
    ```

    or 

    ```
    <xacro:robotiq_gripper
        name="RobotiqGripper"
        prefix=""
        parent="tool0"
        sim_gazebo="true">
        <origin xyz="0 0 0" rpy="0 0 0"/>
    </xacro:robotiq_gripper>
    ```

5. Create urdf file from xacro, need to build project first

  ```
  colcon build --symlink-install
  source install/setup.bash
  xacro src/robot_gripper/urdf/robot_gripper.urdf.xacro > src/robot_gripper/urdf/robot_gripper_final.urdf
  ```

6. Check `urdf`

  ```
  check_urdf src/robot_gripper/urdf/robot_gripper_final.urdf
  ```

  should get 

  ```
  robot name is: robot gripper
  ---------- Successfully Parsed XML ---------------
  root Link: world has 1 child(ren)
      child(1):  base_link
          child(1):  base
          child(2):  base_link_inertia
              child(1):  shoulder_link
                  child(1):  upper_arm_link
                      child(1):  forearm_link
      ...
  ```

## Create Moveit planning

1. Open moveit setup assistant

```
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

2. Click "Create New Moveit Configuration Package" and select the URDF file `robot_gripper_final.urdf` and load, if load good, will see the robot model on the right

![load_urdf](reference/load_urdf.png)

3. On the left tabs, click "Self Collisions". On its bottom of the window, click "linear view", and click "Generate Collision Matrix"

![self_collisions](reference/self_collisions.png)

4. Click "Virtual Joints". Click "Add Virtual Joint". It defines how your robot is attached to the world/reference frame for MoveIt.

Virtual Joint Name: virtual_joint
Child Link: base_link
Parent Frame Name: world
Joint Type: fixed

than click "Save"

![virtual_joints](reference/virtual_joints.png)
![virtual_joints2](reference/virtual_joints2.png)

5. Click "Planning Group". Click "Add group". There are two planning group, one for robot arm, one for gripper.

- Create robot arm planning

Group name: arm
kinematic Solver: kdl_kinematis_plugin/KDLKinematicsPlugin

![planning_group1](reference/planning_group1.png)

Check "Add Kin. Chain"

Base Link: base_link
Tip Link: tool0

![planning_group2](reference/planning_group2.png)

- Create gripper planning

Group name: gripper

![planning_group3](reference/planning_group3.png)

Check "Add Joint", select "finger_joint" or "robotiq_85_left_knuckle_joint"

![planning_group4](reference/planning_group4.png)

Final look like 

![planning_group5](reference/planning_group5.png)

6. Click "Robot Poses". Click "Add group". There are three poses

- arm home, adjust shoulder_lift_joint

![robot_pose1](reference/robot_pose1.png)

- gripper open, finger joint: 0

![robot_pose2](reference/robot_pose2.png)

- gripper close, finger joint: 0.8

![robot_pose3](reference/robot_pose3.png)

7. Click "End Effectors". Click "Add End Effector".

End Effector Name: gripper1
End Effector Group: gripper
Parnet Link: tool0

![end_effector](reference/end_effector.png)

8. Click "ros2_control URDF Modifications". Make sure Add interfaces

![ros2_control_URDF_Modifications](reference/ros2_control_URDF_Modifications.png)

9. Click "ROS2 Controllers", have two controllers

- arm_controller

controller Name: arm_controller
Controller Type: joint_trajectory_controller/JointTrajectoryController

![ROS2_controller1](reference/ROS2_controller1.png)

"Add Planning Group joints"
group: arm

![ROS2_controller2](reference/ROS2_controller2.png)

- gripper_controller

controller Name: gripper_controller
Controller Type: position_controllers/GripperActionController

![ROS2_controller3](reference/ROS2_controller3.png)

"Add Planning Group joints"
group: gripper

![ROS2_controller4](reference/ROS2_controller4.png)

Final
![ROS2_controller5](reference/ROS2_controller5.png)

10. Click "MoveIt Controllers", have two controllers, must be same as ROS2 controller

- robot arm

Controller Name: arm_controller
Controller Type: FllowJointTrajectory
Action Namespace: follow_joint_trajectory
Default: true

![moveit_controller1](reference/moveit_controller1.png)

Add Planning Group Joint
group: arm

![moveit_controller2](reference/moveit_controller2.png)

- Gripper

Controller Name: gripper_controller
Controller Type: GripperCommand
Action Namespace: gripper_cmd
Default: true

![moveit_controller3](reference/moveit_controller3.png)

"Add Planning Group joints"
group: gripper

![moveit_controller4](reference/moveit_controller4.png)

Final

![moveit_controller5](reference/moveit_controller5.png)

[INFO] [launch]: Default logging verbosity is set to INFO
[ERROR] [launch]: Caught exception in launch (see debug for traceback): Caught multiple exceptions when trying to load file of format [py]:
 - ExpatError: not well-formed (invalid token): line 12, column 38
 - InvalidFrontendLaunchFileError: The launch file may have a syntax error, or its format is unknown

11. Click "Configuration Files", generate moveit config into project `moveit_robot_setup`

![configration_file](reference/configration_file.png)


## Test it 

may get error: controller name not match

-  modify the `moveit_robot_setup\config\joint_limits.yaml`

change `has_acceleration_limits` to true and all number should be float
```
has_acceleration_limits: true
max_acceleration: 5.1
```

- fix cannot launch

robot_gripper.ros2_control.xacro in robot_gripper_moveit_setup

  change:
  ```
    <xacro:macro name="robotiq gripper_ros2_control" params="
  ```
  to
  ```
    <xacro:macro name="robotiq_gripper_ros2_control" params="
  ```
  
robot gripper.urdf.xacro in robot_gripper_moveit_setup

  change:
  ```
    <xacro:robot gripper_ros2_control name="FakeSystem" initial_positions_file="$(arg initial_positions_file)"/>
  ```

  to 
  ```
    <xacro:robot_gripper_ros2_control name="FakeSystem" initial_positions_file="$(arg initial_positions_file)"/>
  ```

fix finger cannot plan, remove ros2_control in robot_gripper_final.urdf in robot_gripp
```
  <ros2_control name="RobotiqGripper" type="system">
    <!-- Plugins -->
    <hardware>
      <!-- Set use_dummy to true to connect to a dummy driver for testing purposes. -->
      <param name="use_dummy">false</param>
      <plugin>gz_ros2_control/GazeboSimSystem</plugin>
    </hardware>
    <!-- Joint interfaces -->
    <!-- With Gazebo or Hardware, they handle mimic joints, so we only need this command interface activated -->
    <joint name="robotiq_85_left_knuckle_joint">
      <command_interface name="position"/>
      <state_interface name="position">
        <param name="initial_value">0.7929</param>
      </state_interface>
      <state_interface name="velocity"/>
    </joint>
    <joint name="robotiq_85_right_knuckle_joint">
    </joint>
    <joint name="robotiq_85_left_inner_knuckle_joint">
    </joint>
    <joint name="robotiq_85_right_inner_knuckle_joint">
    </joint>
    <joint name="robotiq_85_left_finger_tip_joint">
    </joint>
    <joint name="robotiq_85_right_finger_tip_joint">
    </joint>
  </ros2_control>
```

1. run test 

```
colcon build
ros2 launch moveit_robot_setup demo.launch.py
```
or 
```
ros2 launch robot_gripper_moveit_setup demo.launch.py
```

- disable loop animation under planned path
