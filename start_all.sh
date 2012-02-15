#!/bin/bash

killall python -KILL # kill running python apps

# nvidia-settings --query=fsaa --verbose

# FSAA Modes Geforce480
#    Valid 'FSAA' Values
#      value - description
#        0   -   Off
#        1   -   2x (2xMS)
#        5   -   4x (4xMS)
#        7   -   8x (4xMS, 4xCS)
#        8   -   16x (4xMS, 12xCS)
#        9   -   8x (4xSS, 2xMS)
#       10   -   8x (8xMS)
#       12   -   16x (8xMS, 8xCS)

export __GL_FSAA_MODE=10 # enable Anti Aliasing
#export __GL_SYNC_TO_VBLANK=1

# start application and device deamon
python main.py $1&
python daemon.py $1&

