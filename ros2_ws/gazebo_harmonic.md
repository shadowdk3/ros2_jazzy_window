### ROS2 Gazebo Harmonic
---------------------------------

## ROS 2 Jazzy + Gazebo, Ubuntu 24.04 inside WSL.

1. Install the ROS Gazebo vendor packages:

```
sudo apt install -y ros-jazzy-ros-gz
sudo apt install -y ros-jazzy-gz-tools-vendor ros-jazzy-gz-sim-vendor
```

2. Source ROS2 env

```
source /opt/ros/jazzy/setup.bash
```

3. Launch the Gazebo window

```
gz sim shapes.sdf
```

![gazebo GUI](reference/gazebo_GUI.png)