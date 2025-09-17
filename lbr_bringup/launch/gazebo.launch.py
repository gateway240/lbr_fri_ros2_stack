from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from lbr_bringup.description import LBRDescriptionMixin
from lbr_bringup.gazebo import GazeboMixin
from lbr_bringup.ros2_control import LBRROS2ControlMixin


def generate_launch_description() -> LaunchDescription:
    ld = LaunchDescription()

    # launch arguments
    ld.add_action(LBRDescriptionMixin.arg_model())
    ld.add_action(LBRDescriptionMixin.arg_robot_name())
    ld.add_action(
        LBRROS2ControlMixin.arg_ctrl()
    )  # Gazebo loads controller configuration through lbr_description/gazebo/*.xacro from lbr_description/ros2_control/lbr_controllers.yaml

    # robot description
    robot_description = LBRDescriptionMixin.param_robot_description(mode="gazebo")

    # robot state publisher
    robot_state_publisher = LBRROS2ControlMixin.node_robot_state_publisher(
        robot_description=robot_description, use_sim_time=True
    )
    ld.add_action(
        robot_state_publisher
    )  # Do not condition robot state publisher on joint state broadcaster as Gazebo uses robot state publisher to retrieve robot description

    # Gazebo
    ld.add_action(GazeboMixin.include_gazebo())
    ld.add_action(GazeboMixin.node_clock_bridge())
    ld.add_action(GazeboMixin.node_create())  # spawns robot in Gazebo through robot_description topic of robot_state_publisher

    # controllers
    joint_state_broadcaster = LBRROS2ControlMixin.node_controller_spawner(
        controller="joint_state_broadcaster"
    )
    ld.add_action(joint_state_broadcaster)
    ld.add_action(
        LBRROS2ControlMixin.node_controller_spawner(
            controller=LaunchConfiguration("ctrl")
        )
    )
    # Include Gazebo ROS launch file to expose /reset_simulation
    gazebo_ros_pkg_share = FindPackageShare('gazebo_ros').find('gazebo_ros')
    gazebo_ros_launch_file = os.path.join(gazebo_ros_pkg_share, 'launch', 'gzserver.launch.py')

    ld.add_action(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_ros_launch_file),
        launch_arguments={'world': 'empty.world'}.items()  # or your custom world
    ))

    return ld
