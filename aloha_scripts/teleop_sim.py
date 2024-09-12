import time
import sys, signal
import IPython
e = IPython.embed

from interbotix_xs_modules.arm import InterbotixManipulatorXS
from interbotix_xs_msgs.msg import JointSingleCommand
from constants import MASTER2PUPPET_JOINT_FN, DT, START_ARM_POSE, MASTER_GRIPPER_JOINT_MID, PUPPET_GRIPPER_JOINT_CLOSE
from robot_utils import torque_on, torque_off, move_arms, move_grippers, get_arm_gripper_positions
import numpy as np
from real_env import make_real_env, get_action

# import json
from multiprocessing.connection import Listener
import rospy

address = ('localhost', 6000)

def prep_robots(master_bot):
    # reboot gripper motors, and set operating modes for all motors
    master_bot.dxl.robot_set_operating_modes("group", "arm", "position")
    master_bot.dxl.robot_set_operating_modes("single", "gripper", "position")
    # puppet_bot.dxl.robot_set_motor_registers("single", "gripper", 'current_limit', 1000) # TODO(tonyzhaozh) figure out how to set this limit
    torque_on(master_bot)

    # move arms to starting position
    start_arm_qpos = START_ARM_POSE[:6]
    move_arms([master_bot], [start_arm_qpos] * 2, move_time=1)
    # move grippers to starting position
    move_grippers([master_bot], [MASTER_GRIPPER_JOINT_MID], move_time=0.5)


def press_to_start(master_bot):
    # press gripper to start data collection
    # disable torque for only gripper joint of master robot to allow user movement
    master_bot.dxl.robot_torque_enable("single", "gripper", False)
    print(f'Close the gripper to start')
    close_thresh = -0.3
    pressed = False
    while not pressed:
        gripper_pos = get_arm_gripper_positions(master_bot)
        if gripper_pos < close_thresh:
            pressed = True
        time.sleep(DT/10)
    torque_off(master_bot)
    print(f'Started!')

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def teleop():
    """ A standalone function for experimenting with teleoperation. No data recording. """
    print("Custom teleop for simulation")
    # For some reason the puppet_bot has to be initialized to activate the master_bot
    puppet_bot_left = InterbotixManipulatorXS(robot_model="vx300s", group_name="arm", gripper_name="gripper", robot_name=f'puppet_left', init_node=True)
    puppet_bot_right = InterbotixManipulatorXS(robot_model="vx300s", group_name="arm", gripper_name="gripper", robot_name=f'puppet_right', init_node=False)

    master_bot_left = InterbotixManipulatorXS(robot_model="wx250s", group_name="arm", gripper_name="gripper", robot_name=f'master_left', init_node=False)
    master_bot_right = InterbotixManipulatorXS(robot_model="wx250s", group_name="arm", gripper_name="gripper", robot_name=f'master_right', init_node=False)

    prep_robots(master_bot_left)
    prep_robots(master_bot_right)

    press_to_start(master_bot_left)
    press_to_start(master_bot_right)

    ### Teleoperation loop
    t = 0
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    gripper_command = JointSingleCommand(name="gripper")
    while (True):
        try:
            with Listener(address, authkey=b'secret password') as listener:
                with listener.accept() as conn:
                    print('connection accepted from', listener.last_accepted)

                    print(f'Action left:')
                    print(f'Action right:')
                    while True:
                        # master_state_joints_left = master_bot_left.dxl.joint_states.position[:6]
                        # master_gripper_joint_left = master_bot_right.dxl.joint_states.position[6]

                        # combined_left = np.array(list(master_state_joints_left) + [master_gripper_joint_left, 0])
                        # combined_right = np.array(list(master_state_joints_left) + [master_gripper_joint_left, 1])

                        action = get_action(master_bot_left, master_bot_right)

                        conn.send(action)

                        if True: #t % 10 == 0:
                            print(LINE_UP, end=LINE_CLEAR)
                            print(LINE_UP, end=LINE_CLEAR)
                            rounded_action = [f"{x:.3f}" for x in action]
                            print(f'Action left: {rounded_action[:7]}')
                            print(f'Action right: {rounded_action[7:]}')

                        # sleep DT
                        time.sleep(DT)
                        t += 1
        except rospy.service.ServiceException:
            print("Service exception. Waiting for new connection.")
            continue
        except ConnectionResetError:
            print("Connection reset. Waiting for new connection.")
            continue
        except ConnectionAbortedError:
            print("Connection aborted. Waiting for new connection.")
            continue
        except ConnectionRefusedError:
            print("Connection refused. Waiting for new connection.")
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue



if __name__=='__main__':
    # side = sys.argv[1]
    teleop()
