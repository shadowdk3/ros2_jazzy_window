from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    ur_type = LaunchConfiguration("ur_type")
    controllers_file = LaunchConfiguration("controllers_file")
    description_file = LaunchConfiguration("description_file")

    # =========================================================
    # Gazebo
    # =========================================================

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py",
            ])
        ),
        launch_arguments={
            "gz_args": "-r empty.sdf",
        }.items(),
    )

    # =========================================================
    # Robot description
    # =========================================================

    robot_description = Command([
        "xacro ",
        description_file,
        " ",
        "ur_type:=",
        ur_type,
        " ",
        "simulation_controllers:=",
        controllers_file,
    ])

    # =========================================================
    # Robot State Publisher
    # For simulation, we want to use the joint states that are published by the robot in Gazebo. 
    # The joint states published by Gazebo have a timestamp that is different from the current ROS time. 
    # This can cause issues with the robot state publisher, which expects the joint states to have a 
    # timestamp that matches the current ROS time.
    # To avoid this issue, we set the ignore_timestamp parameter to True. 
    # This tells the robot state publisher to ignore the timestamp of the joint states and 
    # use the received joint positions instead.
    # =========================================================

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
                "ignore_timestamp": True,
            }
        ],
    )

    # =========================================================
    # Spawn robot
    # =========================================================

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "robot_description",
            "-name",
            "my_ur3",
            "-allow_renaming",
            "true",
        ],
        output="screen",
    )

    # =========================================================
    # Joint State Broadcaster
    # =========================================================

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--param-file",
            controllers_file,
        ],
        output="screen",
    )

    # =========================================================
    # UR3 controller
    # =========================================================

    arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_trajectory_controller",
            "--param-file",
            controllers_file,
        ],
        output="screen",
    )

    # =========================================================
    # Gripper controller
    # =========================================================

    gripper_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "gripper_controller",
            "--param-file",
            controllers_file,
        ],
        output="screen",
    )

    # =========================================================
    # RViz
    # =========================================================

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz",
        output="screen",
        arguments=[
            "-d",
            PathJoinSubstitution([
                FindPackageShare("my_ur3"),
                "rviz",
                "my_ur3.rviz",
            ]),
        ],
        parameters=[
            {
                "use_sim_time": True,
            }
        ],
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            "ur_type",
            default_value="ur3",
        ),

        DeclareLaunchArgument(
            "controllers_file",
            default_value=PathJoinSubstitution([
                FindPackageShare("my_ur3"),
                "config",
                "my_ur3_controllers.yaml",
            ]),
        ),

        DeclareLaunchArgument(
            "description_file",
            default_value=PathJoinSubstitution([
                FindPackageShare("my_ur3"),
                "urdf",
                "my_ur3_gz.urdf.xacro",
            ]),
        ),

        gazebo,

        robot_state_publisher,

        spawn_robot,

        joint_state_broadcaster,

        arm_controller,

        gripper_controller,

        rviz,
    ])