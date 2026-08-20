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


xacro urdf/my_ur3.urdf.xacro name:=my_ur3 ur_type:=ur3 > /tmp/my_ur3.urdf