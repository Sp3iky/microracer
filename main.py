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


# import modules from vr application library
from vr_lib.menu import *
from vr_lib.viewing import *
from vr_lib.simple_navigation import *

# import modules from local library
from lib.scene import *
from lib.navigation import *
from lib.gamelogic import *
from lib.hud import *
from lib.player import *

class Application:

	# constructor
	def __init__(self):

		# class instancies
		self.Menu = Menu()

		self.Scene = Scene(self.Menu)

		self.ViewingSetup = ViewingSetup(self.Scene, self.Menu)

		# init lights (if no lights are defined --> default OpenGL headlight is applied)
		self.Scene.make_light(avango.osg.Vec4(0.0,0.0,0.0,1.0), avango.osg.Vec4(0.65,0.65,0.65,1.0), avango.osg.Vec4(0.2,0.2,0.2,1.0), avango.osg.Vec4(-80,15,-50,1.0))
		self.Scene.make_light(avango.osg.Vec4(0.0,0.0,0.0,1.0), avango.osg.Vec4(0.65,0.65,0.65,1.0), avango.osg.Vec4(0.2,0.2,0.2,1.0), avango.osg.Vec4(60,15,-50,1.0))
		self.Scene.make_light(avango.osg.Vec4(0.0,0.0,0.0,1.0), avango.osg.Vec4(0.65,0.65,0.65,1.0), avango.osg.Vec4(0.2,0.2,0.2,1.0), avango.osg.Vec4(-80,15,40,1.0)) 
		self.Scene.make_light(avango.osg.Vec4(0.0,0.0,0.0,1.0), avango.osg.Vec4(0.65,0.65,0.65,1.0), avango.osg.Vec4(0.2,0.2,0.2,1.0), avango.osg.Vec4(60,15,40,1.0)) 
	
		# init scene objects
		_mat =	avango.osg.make_scale_mat(0.06,0.06,0.06) * \
				avango.osg.make_rot_mat(math.radians(-90.0),1,0,0) * \
				avango.osg.make_trans_mat(0.0,0.0,0.0)
		self.museum = avango.osg.nodes.LoadFile(Filename = "./data/map.obj", Matrix = _mat)
		self.Scene.environment_root.Children.value.append(self.museum)

		# exhibition objects
		_mat = 	avango.osg.make_scale_mat(0.002,0.002,0.002) * \
				avango.osg.make_rot_mat(math.radians(-90.0),1,0,0) * \
				avango.osg.make_trans_mat(-25.0,3.0,0.0)
		self.horse = avango.osg.nodes.LoadFile(Filename = "./data/p1_wedge1.obj", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.horse)

		self.Scene.navigation_transform.Matrix.value = avango.osg.make_trans_mat(5.0,10.0,0.0)


		self.Spacemouse = SpacemouseDevice()

		self.Navigation = Navigation()
		self.Navigation.my_constructor(self.Scene, self.ViewingSetup, self.Spacemouse)
		

		#####  run evaluation and render loop  #####		
		self.ViewingSetup.start_render_loop()
		

Application = Application()


