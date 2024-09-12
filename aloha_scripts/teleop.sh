#!/bin/bash
source activate aloha

if ! pgrep -f "launch_robots.sh" > /dev/null; then
    gnome-terminal -x ./launch_robots.sh
else
    echo "launch_robots.sh is already running."
fi

python one_side_teleop.py left &
python one_side_teleop.py right &
