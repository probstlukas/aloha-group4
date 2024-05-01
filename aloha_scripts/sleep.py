import sys
from interbotix_xs_modules.arm import InterbotixManipulatorXS
from robot_utils import move_arms, torque_on


def sleep(side):
    puppet_bot = InterbotixManipulatorXS(robot_model="vx300s", group_name="arm",
                                         gripper_name="gripper",
                                         robot_name=f'puppet_{side}', init_node=True)

    sleep_position = (0, -1.7, 1.55, 0.12, 0.65, 0)
    rest_position = (
        0,
        puppet_bot.arm.group_info.joint_lower_limits[1],
        puppet_bot.arm.group_info.joint_upper_limits[2],
        0.12,
        0.65,
        0
    )

    torque_on(puppet_bot)

    move_arms([puppet_bot], [sleep_position] * 2, move_time=2)
    move_arms([puppet_bot], [rest_position] * 2, move_time=1)

if __name__ == '__main__':
    side = sys.argv[1]
    sleep(side)
