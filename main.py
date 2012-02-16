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
		_mat =	avango.osg.make_scale_mat(12,12,12) * \
				avango.osg.make_rot_mat(math.pi,1,0,0) * \
				avango.osg.make_trans_mat(-7.0,0.0,-5.0)
		self.museum = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/shader_textured_museum3_small/museum_building.obj", Matrix = _mat)
		self.Scene.environment_root.Children.value.append(self.museum)

		# exhibition objects
		_mat = 	avango.osg.make_scale_mat(1.3,1.3,1.3) * \
				avango.osg.make_rot_mat(math.radians(80.0),0,0,1) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0) * \
				avango.osg.make_trans_mat(1.7,1.2,-14.0)
		self.horse = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/horse.obj", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.horse)

		_mat = 	avango.osg.make_scale_mat(0.0006,0.0006,0.0006) * \
				avango.osg.make_rot_mat(math.radians(135.0),0,0,1) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0) * \
				avango.osg.make_trans_mat(-16.0,0.6,-3.0)
		self.athene = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/athene.3ds", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.athene)

		_mat = 	avango.osg.make_scale_mat(0.028,0.028,0.028) * \
				avango.osg.make_rot_mat(math.radians(60.0),0,0,1) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0) * \
				avango.osg.make_trans_mat(-2.1,1.45,-0.75)
		self.buddha = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/64david-sculpture.3ds", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.buddha)

		_mat = 	avango.osg.make_scale_mat(0.008,0.008,0.008) * \
				avango.osg.make_rot_mat(math.pi,1,0,0) * \
				avango.osg.make_rot_mat(math.pi,0,1,0) * \
				avango.osg.make_trans_mat(4.1,1.0,5.8)
		self.buddha = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/buddha.obj", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.buddha)

		_mat = 	avango.osg.make_scale_mat(0.004,0.004,0.004) * \
				avango.osg.make_rot_mat(math.pi,-1,0,0)	* \
				avango.osg.make_trans_mat(2.15,0.97,-3.55)
		self.chess = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/chess-game.obj", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.chess)

		_mat = 	avango.osg.make_scale_mat(0.14,0.14,0.14) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0)	* \
				avango.osg.make_trans_mat(-1.7,1.0,-17.65)
		self.dino = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/dino.obj", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.dino)

		_mat = 	avango.osg.make_scale_mat(0.055,0.055,0.055) * \
				avango.osg.make_rot_mat(math.pi,1,0,0) * \
				avango.osg.make_rot_mat(math.radians(65.0),0,1,0) * \
				avango.osg.make_trans_mat(-15.4,1.1,-14.25)
		self.shoe = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/shoe.obj", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.shoe)

		_mat = 	avango.osg.make_scale_mat(0.00008,0.00008,0.00008) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0) * \
				avango.osg.make_rot_mat(math.radians(90.0),0,-1,0) * \
				avango.osg.make_trans_mat(-12.5,1.2,-17.8)
		self.ear = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/ear-medical.3ds", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.ear)

		_mat = 	avango.osg.make_scale_mat(0.00013,0.00013,0.00013) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0) * \
				avango.osg.make_rot_mat(math.radians(90.0),0,0,0) * \
				avango.osg.make_trans_mat(-8.7,1.1,-14.0)
		self.boat = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/exhibition/Diesel_Tug.3ds", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.boat)

		_mat = 	avango.osg.make_scale_mat(0.03,0.03,0.03) * \
				avango.osg.make_rot_mat(math.pi*0.5,-1,0,0) * \
				avango.osg.make_rot_mat(math.radians(135),0,1,0) * \
				avango.osg.make_trans_mat(-18.0,0.0,4.0)
		self.passat = avango.osg.nodes.LoadFile(Filename = "/opt/3d_models/cars/passat/passat.3ds", Matrix = _mat)
		self.Scene.object_root.Children.value.append(self.passat)

		self.Scene.navigation_transform.Matrix.value = avango.osg.make_trans_mat(0.0,1.2,3.2)


		self.Spacemouse = SpacemouseDevice()

		self.Navigation = Navigation()
		self.Navigation.my_constructor(self.Scene, self.ViewingSetup, self.Spacemouse)
		

		#####  run evaluation and render loop  #####		
		self.ViewingSetup.start_render_loop()
		

Application = Application()


