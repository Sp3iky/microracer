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

import avango
import avango.osg
import avango.daemon
import sys
import math
import socket

# viewing setup mode
gl_viewing_setup = "desktop" # default setup
if len(sys.argv) >= 2: # check for further command line options
	gl_viewing_setup = str(sys.argv[1])

_supported_viewing_setups = ["desktop", "anaglyph", "checkerboard"]
if _supported_viewing_setups.count(gl_viewing_setup) == 0: # check if viewing setup is supported
	print "Viewing Setup NOT supported!"
	sys.exit(1) # terminate application


	
_host_name = socket.gethostname()

if _host_name == "argos" or _host_name == "andromeda" or _host_name == "boreas" or _host_name == "demeter" or _host_name == "agenor" or _host_name == "daedalos" or _host_name == "helios" or _host_name == "achill": # monitor: Dell
	gl_display_configuration = 0

elif _host_name == "atlas": # monitor: Samsung SyncMaster 226BW
	gl_display_configuration = 1

elif _host_name == "apollo": # monitor: Samsung SyncMaster 2494
	gl_display_configuration = 2
	
elif _host_name == "nestor": # stereo-tv: Samsung 56'
	gl_display_configuration = 3

elif _host_name == "eris": # stereo-tv: table
	gl_display_configuration = 5



#gl_display_configuration = 1 # choose your own display

	
if gl_display_configuration == 0: # monitor: Dell

	gl_headtracking_flag		= 	False
	gl_physical_screen_width 	= 	0.59	
	gl_physical_screen_height 	= 	0.335
	gl_pixels_width 			= 	2560
	gl_pixels_height 			= 	1440
	gl_wanted_position_x		= 	0
	gl_wanted_position_y		= 	0
	gl_screen_transform 		= 	avango.osg.make_ident_mat()
	gl_eye_transform 			= 	avango.osg.make_trans_mat(0.0,0.0,0.5) # default head position 50cm in front of display
	gl_transmitter_offset 		= 	avango.osg.make_trans_mat(-0.31,-0.27,0.55)
	
	gl_ground_flag				= 	False
	gl_ground_plane_transform	= 	avango.osg.make_scale_mat(gl_physical_screen_width * 1.4, gl_physical_screen_width * 1.4, 1.0) * \
									avango.osg.make_rot_mat(math.radians(90),-1,0,0) * \
									avango.osg.make_trans_mat(0.0, gl_physical_screen_height * -0.5, 0.0)
	gl_background_color = avango.osg.Vec4(0.3, 0.3, 0.3, 1.0)

	print "display configuration: Monitor DELL"


elif gl_display_configuration == 1: # monitor: Samsung SyncMaster 226BW

	gl_headtracking_flag		= 	False
	gl_physical_screen_width 	= 	0.47
	gl_physical_screen_height 	= 	0.3
	gl_pixels_width 			= 	1680
	gl_pixels_height 			= 	1050
	gl_wanted_position_x		= 	0
	gl_wanted_position_y		= 	0
	gl_screen_transform 		= 	avango.osg.make_ident_mat()
	gl_eye_transform 			= 	avango.osg.make_trans_mat(0.0,0.0,0.5)
	gl_transmitter_offset 		= 	avango.osg.make_ident_mat()

	gl_ground_flag				= 	False
	gl_ground_plane_transform	= 	avango.osg.make_scale_mat(gl_physical_screen_width * 1.4, gl_physical_screen_width * 1.4, 1.0) * \
									avango.osg.make_rot_mat(math.radians(90),-1,0,0) * \
									avango.osg.make_trans_mat(0.0, gl_physical_screen_height * -0.5, 0.0)	
	gl_background_color = avango.osg.Vec4(0.3, 0.3, 0.3, 1.0)

	print "display configuration: Monitor Samsung SyncMaster 226BW"


elif gl_display_configuration == 2: # monitor: Samsung SyncMaster 2494

	gl_headtracking_flag		= 	False
	gl_physical_screen_width 	= 	0.53
	gl_physical_screen_height 	= 	0.3
	gl_pixels_width 			= 	1920
	gl_pixels_height 			= 	1080
	gl_wanted_position_x		= 	0
	gl_wanted_position_y		= 	0
	gl_screen_transform 		= 	avango.osg.make_ident_mat()
	gl_eye_transform 			= 	avango.osg.make_trans_mat(0.0,0.0,0.5) # default head position 50cm in front of display
	gl_transmitter_offset 		= 	avango.osg.make_ident_mat()

	gl_ground_flag				= 	False
	gl_ground_plane_transform	= 	avango.osg.make_scale_mat(gl_physical_screen_width * 1.4, gl_physical_screen_width * 1.4, 1.0) * \
									avango.osg.make_rot_mat(math.radians(90),-1,0,0) * \
									avango.osg.make_trans_mat(0.0, gl_physical_screen_height * -0.5, 0.0)
	gl_background_color = avango.osg.Vec4(0.3, 0.3, 0.3, 1.0)

	print "display configuration: Monitor Samsung SyncMaster 2494"

elif gl_display_configuration == 3: # stereo-tv: samsung 56'

	gl_headtracking_flag		= 	True
	gl_physical_screen_width 	= 	1.23
	gl_physical_screen_height 	= 	0.685
	gl_pixels_width 			= 	1920
	gl_pixels_height 			= 	1080
	gl_wanted_position_x		= 	1680
	gl_wanted_position_y		= 	0
	gl_screen_transform 		= 	avango.osg.make_ident_mat()
	gl_eye_transform 			= 	avango.osg.make_trans_mat(0.0,0.0,0.6) # default head position 60cm in front of display
	gl_transmitter_offset 		= 	avango.osg.make_trans_mat(0.0,-0.2,1.0)
	gl_ground_flag				= 	True
	gl_ground_plane_transform	= 	avango.osg.make_scale_mat(gl_physical_screen_width * 1.4, gl_physical_screen_width * 1.4, 1.0) * \
									avango.osg.make_rot_mat(math.radians(90),-1,0,0) * \
									avango.osg.make_trans_mat(0.0, gl_physical_screen_height * -0.5, 0.0)
	gl_background_color = avango.osg.Vec4(0.3, 0.3, 0.3, 1.0)

	print "display configuration: Stereo-TV Samsung 56inch"


elif gl_display_configuration == 5: # stereo-tv: table

	gl_headtracking_flag		= 	True
	gl_physical_screen_width 	= 	1.44
	gl_physical_screen_height 	= 	0.8
	gl_pixels_width 			= 	1920
	gl_pixels_height 			= 	1080
	gl_wanted_position_x		= 	1920
	gl_wanted_position_y		= 	0
	gl_screen_transform 		= 	avango.osg.make_rot_mat(math.pi*0.5,1,0,0) * \
									avango.osg.make_rot_mat(math.pi,0,0,1)
	gl_eye_transform 			= 	avango.osg.make_trans_mat(0.0,0.55,0.5) # default head position relative to display
	gl_transmitter_offset 		= 	avango.osg.make_trans_mat(0.0,0.04,0.)
	gl_ground_flag				= 	True
	gl_ground_plane_transform	= 	avango.osg.make_scale_mat(gl_physical_screen_width * 0.75, gl_physical_screen_height * 0.75, 1.0) * \
									avango.osg.make_rot_mat(math.radians(90),-1,0,0)
	gl_background_color = avango.osg.Vec4(0.3, 0.3, 0.3, 1.0)

	print "display configuration: Stereo-TV Table"


gl_device_service = avango.daemon.DeviceService()

