#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELATIVE_PATH="../../aloha_platform_simulation/examples"

gnome-terminal -x bash -c "./teleop_sim.sh; exec bash"

sleep 10s && gnome-terminal --working-directory="${SCRIPT_DIR}/${RELATIVE_PATH}" -x bash -c "./teleop.sh; exec bash"