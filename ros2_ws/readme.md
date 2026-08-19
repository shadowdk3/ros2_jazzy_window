### ROS2 JAZZY
---------------------------------
@ reference
https://docs.ros.org/en/jazzy/Installation/Windows-Install-Binary.html#system-requirements

* Winodw 10
* Ubuntu 24.04

### Window 10

## Install pixi

```
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

## Download and install dependencies

```
md C:\pixi_ws
cd C:\pixi_ws
irm https://raw.githubusercontent.com/ros2/ros2/refs/heads/jazzy/pixi.toml -OutFile pixi.toml
pixi install
```

## Source the pixi enviroment

```
cd C:\pixi_ws
pixi shell
```

## Source ROS2 enviroment

```
call C:\pixi_ws\ros2-windows\local_setup.bat
```

### Ubuntu 24.04

## install Windows Subsystem for Linux (WSL) on Windows 10

1. Install ubuntu 24.04
```
wsl --install -d Ubuntu-24.04
```

2. Launch Ubuntu

```
wsl
```

## Install ROS2

1. First ensure that the Ubuntu Universe repository is enabled.

```
sudo apt install software-properties-common
sudo add-apt-repository universe
```
2. Install require 

```
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb

sudo apt update && sudo apt install ros-dev-tools
```

3. Install jazzy

```
sudo apt install ros-jazzy-desktop
```

4. Run test

```
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_cpp talker
```

In another terminal

```
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_py listener
```