#!/usr/bin/python
# -*- Mode:Python -*-

##########################################################################
#                                                                        #
# This file is part of Avango.                                           #
#                                                                        #
# Copyright 1997 - 2008 Fraunhofer-Gesellschaft zur Foerderung der       #
# angewandten Forschung (FhG), Munich, Germany.                          #
#                                                                        #
# Avango is free software: you can redistribute it and/or modify         #
# it under the terms of the GNU Lesser General Public License as         #
# published by the Free Software Foundation, version 3.                  #
#                                                                        #
# Avango is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the           #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU Lesser General Public       #
# License along with Avango. If not, see <http://www.gnu.org/licenses/>. #
#                                                                        #
# Avango is a trademark owned by FhG.                                    #
#                                                                        #
##########################################################################


import avango.daemon
import os


# import modules from local library
from lib.globals import *

# functions
def init_pst_tracking():

	# create instance of DTrack
	_pst = avango.daemon.DTrack()
	_pst.port = "5002" # PST port
	
	# head tracking
	_pst.stations[1] = avango.daemon.Station('tracking-head')
	
	device_list.append(_pst)
	print "PST Tracking started!"



def init_spacemouse():

	_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"3Dconnexion SpaceNavigator\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

	if len(_string) == 0:
		_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"3Dconnexion SpaceTraveler USB\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()
    
	if len(_string) > 0:	
		_string = _string.split()[0]
	
		_spacemouse = avango.daemon.HIDInput()
		_spacemouse.station = avango.daemon.Station('device-spacemouse') # create a station to propagate the input events
		_spacemouse.device = _string

		# map incoming spacemouse events to station values
		_spacemouse.values[0] = "EV_ABS::ABS_X"   # trans X
		_spacemouse.values[1] = "EV_ABS::ABS_Y"   # trans Y
		_spacemouse.values[2] = "EV_ABS::ABS_Z"   # trans Z
		_spacemouse.values[3] = "EV_ABS::ABS_RX"  # rotate X
		_spacemouse.values[4] = "EV_ABS::ABS_RY"  # rotate Y
		_spacemouse.values[5] = "EV_ABS::ABS_RZ"  # rotate Z

		# buttons
		_spacemouse.buttons[0] = "EV_KEY::BTN_0" # left button
		_spacemouse.buttons[1] = "EV_KEY::BTN_1" # right button

		device_list.append(_spacemouse)
		print "SpaceMouse started at:", _string

	else:
		print "SpaceMouse NOT found !"



def init_keyboard():

	_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"HID 046a:0011\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

	if len(_string) == 0:
		_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"Cherry GmbH\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

	if len(_string) == 0:
		_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"Logitech Logitech USB Keyboard\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

	if len(_string) > 0:

		_string = _string.split()[0]

		_keyboard = avango.daemon.HIDInput()
		_keyboard.station = avango.daemon.Station('device-keyboard')
		_keyboard.device = _string

		# map incoming events to station values
		_keyboard.buttons[0] = "EV_KEY::KEY_SPACE"
		_keyboard.buttons[1] = "EV_KEY::KEY_N"
		_keyboard.buttons[2] = "EV_KEY::KEY_C"
		_keyboard.buttons[3] = "EV_KEY::KEY_M"
		_keyboard.buttons[4] = "EV_KEY::KEY_R"
		_keyboard.buttons[5] = "EV_KEY::KEY_G"
		_keyboard.buttons[6] = "EV_KEY::KEY_D"
		_keyboard.buttons[7] = "EV_KEY::KEY_F"
		_keyboard.buttons[8] = "EV_KEY::KEY_LEFT"
		_keyboard.buttons[9] = "EV_KEY::KEY_RIGHT"
		
		
		device_list.append(_keyboard)
		print "Keyboard started at:", _string

	else:
		print "Keyboard NOT found !"


def init_mouse():

	_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"Logitech USB-PS/2 Optical Mouse\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

	if len(_string) == 0:
		_string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"Logitech USB Optical Mouse\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

	if len(_string) > 0:

		_string = _string.split()[0]

		_mouse = avango.daemon.HIDInput()
		_mouse.station = avango.daemon.Station('device-mouse')
		_mouse.device = _string

		# map incoming events to station values
		_mouse.buttons[0] = "EV_KEY::BTN_LEFT"
		_mouse.buttons[1] = "EV_KEY::BTN_RIGHT"

		device_list.append(_mouse)
		print "Mouse started at:", _string

	else:
		print "Mouse NOT found !"


device_list = []

# init respective tracking system
if gl_viewing_setup == "desktop" or gl_viewing_setup == "anaglyph" or gl_viewing_setup == "checkerboard":
		
	init_pst_tracking()

# init input devices
init_spacemouse()
init_keyboard()
init_mouse()

	
#avango/trunk/avango-daemon/src/avango/daemon/LinuxEvent.cpp

# start daemon (will enter the main loop)
avango.daemon.run(device_list)
