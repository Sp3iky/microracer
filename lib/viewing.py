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

import avango.osg.viewer
import avango.daemon
import math
import sys

# import modules from local library
from lib.globals import *

class ViewingSetup:

	# contructor
	def __init__(self, SCENE, MENU):
		
		# init viewing setup
		if gl_viewing_setup == "desktop":
			self.setup = DesktopSetup(SCENE)
	
		elif gl_viewing_setup == "minicave":
			self.setup = MiniCaveSetup(SCENE)
	
		else: # viewing setup not supported

			print "Viewing Setup [{0}] NOT supported".format(gl_viewing_setup)
			sys.exit(1) # terminate application
		
		
		# reference
		self.viewer = self.setup.viewer
		self.events = self.setup.events


		# init mouse interaction with application menus
		MENU.init_mouse_menu_interaction(SCENE.navigation_transform, self.setup)

	# functions
	def start_render_loop(self):

		self.viewer.frame() # render a frame
		self.viewer.StatsMode.value = 1 # enable frame rate visualization
		self.viewer.ThreadingModel.value = 2

		self.viewer.run() # start render loop


class DesktopSetup:

	# contructor
	def __init__(self, SCENE):

		# init window
		self.window = avango.osg.viewer.nodes.GraphicsWindow()
		self.window.ScreenIdentifier.value = ":0.0"
		self.window.AutoHeight.value = False
		self.window.StereoMode.value = avango.osg.viewer.stereo_mode.STEREO_MODE_NONE
		
		# screen parameters
		self.window.WantedWidth.value = gl_pixels_width
		self.window.WantedHeight.value = gl_pixels_height
		self.window.WantedPositionX.value = gl_wanted_position_x
		self.window.WantedPositionY.value = gl_wanted_position_y
		self.window.RealScreenWidth.value = gl_physical_screen_width
		self.window.RealScreenHeight.value = gl_physical_screen_height

		# init camera
		self.camera = avango.osg.viewer.nodes.Camera(Window = self.window)
		self.camera.ScreenTransform.value = gl_screen_transform
		self.camera.BackgroundColor.value = gl_background_color

		# init field connections
		self.camera.ViewerTransform.connect_from(SCENE.navigation_transform.Matrix)

		if gl_headtracking_flag == True:
			self.tracking_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService(), Station = "tracking-head", TransmitterOffset = gl_transmitter_offset) # init tracking sensor
			self.camera.EyeTransform.connect_from(self.tracking_sensor.Matrix)

		else:
			self.camera.EyeTransform.value = gl_eye_transform # fixed head position

		# init viewer
		self.viewer = avango.osg.viewer.nodes.Viewer(Scene = SCENE.root, MasterCamera = self.camera)

		# init simple mouse events
		self.events = avango.osg.viewer.nodes.EventFields(View = self.viewer)

		self.window.DragEvent.connect_from(self.events.DragEvent)
		self.window.MoveEvent.connect_from(self.events.MoveEvent)
		self.window.ToggleFullScreen.connect_from(self.events.KeyAltReturn)


		self.init_ground_plane(SCENE)

	# functions
	def init_ground_plane(self, SCENE):
		if gl_ground_flag == True:
			self.ground_panel = avango.osg.nodes.Panel(PanelColor = avango.osg.Vec4(0.5,0.5,0.3,0.75), Width = 1.0, Height = 1.0)
			self.ground_geode = avango.osg.nodes.LayerGeode(Drawables = [self.ground_panel], StateSet = avango.osg.nodes.StateSet(BlendMode = 1, LightingMode = 0, RenderingHint = 2))
			self.ground_transform = avango.osg.nodes.MatrixTransform(Children = [self.ground_geode])
			self.ground_transform.Matrix.value = gl_ground_plane_transform
			SCENE.root.Children.value.append(self.ground_transform)


class MiniCaveSetup:

	# contructor
	def __init__(self, SCENE):

		# parameters
		self.eye_offset = 0.065

		# init display 1 
		self.window1 = avango.osg.viewer.nodes.GraphicsWindow()
		self.window1.ScreenIdentifier.value = ":0.0"
		self.window1.Decoration.value = False
		self.window1.AutoHeight.value = False
		self.window1.StereoMode.value = avango.osg.viewer.stereo_mode.STEREO_MODE_ANAGLYPHIC
		
		# screen parameters
		self.window1.WantedWidth.value = gl_pixels_width
		self.window1.WantedHeight.value = gl_pixels_height
		self.window1.WantedPositionX.value = gl_wanted_position_x
		self.window1.WantedPositionY.value = gl_wanted_position_y
		self.window1.RealScreenWidth.value = gl_physical_screen_width
		self.window1.RealScreenHeight.value = gl_physical_screen_height

		# init camera
		self.camera1 = avango.osg.viewer.nodes.Camera(Window = self.window1)
		self.camera1.EyeOffset.value = self.eye_offset * 0.5
		self.camera1.ScreenTransform.value = gl_screen_transform
		self.camera1.BackgroundColor.value = gl_background_color

		# init display 2
		self.window2 = avango.osg.viewer.nodes.GraphicsWindow()
		self.window2.ScreenIdentifier.value = ":0.1"
		self.window2.Decoration.value = False
		self.window2.AutoHeight.value = False
		self.window2.StereoMode.value = avango.osg.viewer.stereo_mode.STEREO_MODE_ANAGLYPHIC
	
		# screen parameters
		self.window2.WantedWidth.value = gl_pixels_width
		self.window2.WantedHeight.value = gl_pixels_height
		self.window2.WantedPositionX.value = 0
		self.window2.WantedPositionY.value = 0
		self.window2.RealScreenWidth.value = gl_physical_screen_width
		self.window2.RealScreenHeight.value = gl_physical_screen_height

		# init camera
		self.camera2 = avango.osg.viewer.nodes.Camera(Window = self.window2)
		self.camera2.EyeOffset.value = self.eye_offset * 0.5
		self.camera2.ScreenTransform.value = gl_screen_transform2
		self.camera2.BackgroundColor.value = gl_background_color

		# init display 3
		self.window3 = avango.osg.viewer.nodes.GraphicsWindow()
		self.window3.ScreenIdentifier.value = ":0.2"
		self.window3.Decoration.value = False
		self.window3.AutoHeight.value = False
		self.window3.StereoMode.value = avango.osg.viewer.stereo_mode.STEREO_MODE_ANAGLYPHIC
	
		# screen parameters
		self.window3.WantedWidth.value = gl_pixels_width
		self.window3.WantedHeight.value = gl_pixels_height
		self.window3.WantedPositionX.value = 0
		self.window3.WantedPositionY.value = 0
		self.window3.RealScreenWidth.value = gl_physical_screen_width
		self.window3.RealScreenHeight.value = gl_physical_screen_height

		# init camera
		self.camera3 = avango.osg.viewer.nodes.Camera(Window = self.window3)
		self.camera3.EyeOffset.value = self.eye_offset * 0.5
		self.camera3.ScreenTransform.value = avango.osg.make_rot_mat(math.radians(45),0,1,0) * \
									avango.osg.make_trans_mat(-0.51,0.0,0.28)
		self.camera3.BackgroundColor.value = gl_background_color


		# init field connections
		self.camera1.ViewerTransform.connect_from(SCENE.navigation_transform.Matrix)
		self.camera2.ViewerTransform.connect_from(SCENE.navigation_transform.Matrix)
		self.camera3.ViewerTransform.connect_from(SCENE.navigation_transform.Matrix)

		if gl_headtracking_flag == True:
			self.tracking_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService(), Station = "tracking-head", TransmitterOffset = gl_transmitter_offset) # init tracking sensor
			self.camera1.EyeTransform.connect_from(self.tracking_sensor.Matrix)
			self.camera2.EyeTransform.connect_from(self.tracking_sensor.Matrix)
			self.camera3.EyeTransform.connect_from(self.tracking_sensor.Matrix)

		else:
			self.camera1.EyeTransform.value = gl_eye_transform # fixed head position
			self.camera2.EyeTransform.value = gl_eye_transform # fixed head position
			self.camera3.EyeTransform.value = gl_eye_transform # fixed head position


		# init viewer
		self.viewer = avango.osg.viewer.nodes.Viewer(Scene = SCENE.root, MasterCamera = self.camera1, SlaveCameras = [self.camera2, self.camera3])

		# init simple mouse events
		self.events = avango.osg.viewer.nodes.EventFields(View = self.viewer)

		self.window1.DragEvent.connect_from(self.events.DragEvent)
		self.window1.MoveEvent.connect_from(self.events.MoveEvent)
		self.window1.ToggleFullScreen.connect_from(self.events.KeyAltReturn)


		self.init_ground_plane(SCENE)

	# functions
	def init_ground_plane(self, SCENE):
		if gl_ground_flag == True:
			self.ground_panel = avango.osg.nodes.Panel(PanelColor = avango.osg.Vec4(0.5,0.5,0.3,0.75), Width = 1.0, Height = 1.0)
			self.ground_geode = avango.osg.nodes.LayerGeode(Drawables = [self.ground_panel], StateSet = avango.osg.nodes.StateSet(BlendMode = 1, LightingMode = 0, RenderingHint = 2))
			self.ground_transform = avango.osg.nodes.MatrixTransform(Children = [self.ground_geode])
			self.ground_transform.Matrix.value = gl_ground_plane_transform
			SCENE.root.Children.value.append(self.ground_transform)

