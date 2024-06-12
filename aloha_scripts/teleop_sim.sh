#!/bin/bash

gnome-terminal -x ./launch_robots.sh

source activate aloha
python teleop_sim.py