### Gazebo UR3
---------------------------------

* ROS2 Jazzy
* Gazebo Harmonic
* WSL

1. Install require

```
sudo apt install -y ros-jazzy-ros-gz \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-xacro \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    ros-jazzy-moveit \
    ros-jazzy-ur-robot-driver \
    ros-jazzy-ur-moveit-config


```

2. Cloned the Universal Robots Universal_Robots_ROS2_Description repository

```
git clone -b jazzy https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git
```

3. Build and test

```
colcon build --symlink-install
ros2 launch ur_description view_ur.launch.xml ur_type:=ur3
```

4. Simulate gazebo and rviz at the same time

```
git clone -b jazzy https://github.com/UniversalRobots/Universal_Robots_ROS2_GZ_Simulation.git
ros2 launch ur_simulation_gz ur_sim_control.launch.py ur_type:=ur3
```

5. Test movement

```
ros2 topic pub --once \
/scaled_joint_trajectory_controller/joint_trajectory \
trajectory_msgs/msg/JointTrajectory \
"{
  joint_names: [
    'shoulder_pan_joint',
    'shoulder_lift_joint',
    'elbow_joint',
    'wrist_1_joint',
    'wrist_2_joint',
    'wrist_3_joint'
  ],
  points: [
    {
      positions: [0.2, -1.0, 1.0, -1.5, -1.0, 0.2],
      time_from_start: {sec: 3}
    }
  ]
}"
```

create my_ur3.urdf.xarco to call ur.urdf.xacro
<?xml version="1.0"?>

<robot xmlns:xacro="http://wiki.ros.org/xacro"
       name="my_ur3">

  <xacro:include filename="$(find ur_description)/urdf/ur.urdf.xacro"/>

</robot>

xacro urdf/my_ur3.urdf.xacro name:=my_ur3 ur_type:=ur3 > /tmp/my_ur3.urdf

check exit
ls -lh /tmp/my_ur3.urdf

head -20 /tmp/my_ur3.urdf

Validate the URDF
check_urdf /tmp/my_ur3.urdf

Check the six joints
grep '<joint ' /tmp/my_ur3.urdf

Check the links
grep '<link ' /tmp/my_ur3.urdf | grep 'name='

create a Launch file
ros2 launch my_ur3 display.launch.py


ros2 run joint_state_publisher_gui joint_state_publisher_gui


ros2 run xacro xacro \
~/ros2_jazzy_window/ros2_ws/src/my_ur3/urdf/my_ur3.urdf.xacro \
> /tmp/my_ur3.urdf

ros2 action send_goal \
/joint_trajectory_controller/follow_joint_trajectory \
control_msgs/action/FollowJointTrajectory \
"{
  trajectory: {
    joint_names: [
      'shoulder_pan_joint',
      'shoulder_lift_joint',
      'elbow_joint',
      'wrist_1_joint',
      'wrist_2_joint',
      'wrist_3_joint'
    ],
    points: [
      {
        positions: [0.3, -1.0, 1.0, -1.5, 0.0, 0.0],
        time_from_start: {sec: 5}
      }
    ]
  }
}"

Control the gripper with its forward position controller. Send the same
opening value to both fingers in meters.

```
ros2 topic pub --once \\
/gripper_controller/commands \\
std_msgs/msg/Float64MultiArray \\
'{data: [0.02, 0.02]}'
```

Use a value between `0.0` (closed) and `0.04` (open). Confirm that the
controller is active with:

```
ros2 control list_controllers
```