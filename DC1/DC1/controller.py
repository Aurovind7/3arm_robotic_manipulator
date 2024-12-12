#!/usr/bin/env python3
import sys
import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from rclpy.node import Node

class ArmController(Node):

    def __init__(self):
        super().__init__('arm_controller')
        self._trajectory_client = ActionClient(self, FollowJointTrajectory, '/arm_trajectory_controller/follow_joint_trajectory')

    def execute_trajectory(self, ang1, ang2, ang3):
        trajectory_goal = FollowJointTrajectory.Goal()

        joint_labels = [
            "joint_a", "joint_b", "joint_c"
        ]

        points = []
        start_point = JointTrajectoryPoint()
        start_point.positions = [0.0] * 3
        points.append(start_point)

        end_point = JointTrajectoryPoint()
        end_point.time_from_start = Duration(seconds=2, nanoseconds=0).to_msg()
        end_point.positions = [ang1, ang2, ang3]
        points.append(end_point)

        trajectory_goal.goal_time_tolerance = Duration(seconds=3, nanoseconds=0).to_msg()
        trajectory_goal.trajectory.joint_names = joint_labels
        trajectory_goal.trajectory.points = points

        self._trajectory_client.wait_for_server()
        self._send_trajectory_future = self._trajectory_client.send_goal_async(
            trajectory_goal, feedback_callback=self.trajectory_feedback_callback)
        self._send_trajectory_future.add_done_callback(self.trajectory_response_callback)

    def trajectory_response_callback(self, future):
        trajectory_handle = future.result()
        if not trajectory_handle.accepted:
            self.get_logger().info('Trajectory rejected :(')
            return

        self.get_logger().info('Trajectory accepted :)')

        self._get_result_future = trajectory_handle.get_result_async()
        self._get_result_future.add_done_callback(self.trajectory_result_callback)

    def trajectory_result_callback(self, future):
        trajectory_result = future.result().result
        self.get_logger().info('Result: ' + str(trajectory_result))
        rclpy.shutdown()

    def trajectory_feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback


def main(args=None):

    rclpy.init()
    trajectory_client = ArmController()

    if len(sys.argv) < 4:
        print("Please provide joint positions as command-line arguments.")
        return

    ang1 = float(sys.argv[1])
    ang2 = float(sys.argv[2])
    ang3 = float(sys.argv[3])

    trajectory_client.execute_trajectory(ang1, ang2, ang3)
    rclpy.spin(trajectory_client)


if __name__ == '__main__':
    main()
