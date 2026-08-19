### ROS2 JAZZY
---------------------------------
@ reference
https://docs.ros.org/en/jazzy/Installation/Windows-Install-Binary.html#system-requirements

* winodw 10

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

