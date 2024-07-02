#!/bin/bash

if ! pgrep -f "launch_robots.sh" > /dev/null; then
    gnome-terminal -x ./launch_robots.sh
else
    echo "launch_robots.sh is already running."
fi

source activate aloha
python teleop_sim.py
