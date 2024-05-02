#!/bin/bash

source /opt/ros/noetic/setup.sh && source /shared/interbotix_ws/devel/setup.sh
roslaunch aloha 4arms_teleop.launch
