
import sys
import avango
import math

class Scene:

	# constructor	
	def __init__(self, MENU):			

		# references
		self.MENU = MENU
		
		# variables
		self.lightsources = [] # list with all lightsources
		self.light_number = 0

		# setup shader (phong lighting + texturing + diffuse color override)
		self.environment_vshader = avango.osg.nodes.Shader(Type = avango.osg.shadertype.VERTEX, FileName = "/opt/avango/vr_application_lib/shader/phong_material_override_walls.vert")
		self.environment_fshader = avango.osg.nodes.Shader(Type = avango.osg.shadertype.FRAGMENT, FileName = "/opt/avango/vr_application_lib/shader/phong_material_override_walls.frag")

		self.environment_prog = avango.osg.nodes.Program(ShaderList = [self.environment_vshader, self.environment_fshader])

		# environment shader states
		self.environment_uniform1 = avango.osg.nodes.Uniform(Values = [0], Type = avango.osg.uniformtype.INT, UniformName = "color_map")
		self.environment_uniform2 = avango.osg.nodes.Uniform(Values = [1], Type = avango.osg.uniformtype.INT, UniformName = "color_map2")
		self.environment_uniform3 = avango.osg.nodes.Uniform(Values = [1], Type = avango.osg.uniformtype.INT, UniformName = "NumLights")		
		
		self.environment_state = avango.osg.nodes.StateSet(RescaleNormalMode = 1, NormalizeMode = 1, CullFaceMode = 0, Program = self.environment_prog, Uniforms = [self.environment_uniform1, self.environment_uniform2, self.environment_uniform3])


		# setup shader (phong lighting + texturing + diffuse color override)
		self.object_vshader = avango.osg.nodes.Shader(Type = avango.osg.shadertype.VERTEX, FileName = "/opt/avango/vr_application_lib/shader/phong_material_override.vert")
		self.object_fshader = avango.osg.nodes.Shader(Type = avango.osg.shadertype.FRAGMENT, FileName = "/opt/avango/vr_application_lib/shader/phong_material_override.frag")

		self.object_prog = avango.osg.nodes.Program(ShaderList = [self.object_vshader, self.object_fshader])

		# global shader states for all scene elements
		self.object_uniform1 = avango.osg.nodes.Uniform(Values = [1], Type = avango.osg.uniformtype.INT, UniformName = "NumLights")		
		self.object_uniform2 = avango.osg.nodes.Uniform(Values = [0], Type = avango.osg.uniformtype.INT, UniformName = "color_map")
		
		self.object_state = avango.osg.nodes.StateSet(RescaleNormalMode = 1, NormalizeMode = 1, CullFaceMode = 0, Program = self.object_prog, Uniforms = [self.object_uniform1, self.object_uniform2])

		# scene structure
		self.root = avango.osg.nodes.Group() # root node

		self.environment_root = avango.osg.nodes.Group(StateSet = self.environment_state, Name = "environment_root")
		self.root.Children.value.append(self.environment_root)
		
		self.object_root = avango.osg.nodes.Group(StateSet = self.object_state, Name = "object_root")
		self.root.Children.value.append(self.object_root)
														
		self.interface_root = avango.osg.nodes.Group(StateSet = self.object_state, Name = "interface_root")
		self.root.Children.value.append(self.interface_root)
																				
		self.navigation_transform = avango.osg.nodes.MatrixTransform(Name = "navigation_transform")
		self.root.Children.value.append(self.navigation_transform)

		self.menu_navigation_transform = avango.osg.nodes.MatrixTransform(Name = "menu_navigation_transform")
		self.menu_navigation_transform.Matrix.connect_from(self.navigation_transform.Matrix)
		self.root.Children.value.append(self.menu_navigation_transform)

		self.menu_navigation_transform.Children.value.append(MENU.menu_transform) # append menu root node to navigation node
	

	# functions
	def make_light(self, AMBIENT, DIFFUSE, SPECULAR, POSITION):

		_light = avango.osg.nodes.Light(LightNum = self.light_number, Ambient = AMBIENT, Diffuse = DIFFUSE, Specular = SPECULAR, Position = POSITION)		
		_lightsource = avango.osg.nodes.LightSource(Light = _light, Children = [self.object_root])

		if self.light_number == 0:
			self.root.Children.value.remove(self.object_root)
			self.root.Children.value.append(_lightsource) # append first light to the scene
		else:
			self.lightsources[self.light_number-1].Children.value = [_lightsource] # append further lights

		self.lightsources.append(_lightsource)
		self.light_number += 1
		
		self.environment_uniform3.Values.value = [self.light_number] # forward light number to shader
		self.object_uniform1.Values.value = [self.light_number] # forward light number to shader
		
		# light source visualization
		_geometry = avango.osg.nodes.Sphere(DetailRatio = 0.4, Color = _light.Diffuse.value)
		_geometry.Matrix.value = 	avango.osg.make_scale_mat(0.05,0.05,0.05) * \
						avango.osg.make_trans_mat(_light.Position.value.x, _light.Position.value.y, _light.Position.value.z)
		
		_geometry.StateSet.value = avango.osg.nodes.StateSet(WireframeMode = 1, RescaleNormalMode = 1, NormalizeMode = 1, Program = avango.osg.nodes.Program(ShaderList = [
																								avango.osg.nodes.Shader(Name = "VertexShader", Type = avango.osg.shadertype.VERTEX,ShaderSource = "void main() { gl_Position = ftransform(); }"),
																								avango.osg.nodes.Shader(Name = "VertexShader", Type = avango.osg.shadertype.FRAGMENT,ShaderSource = "void main() { gl_FragColor = gl_FrontMaterial.diffuse; }")
																		]))
		self.root.Children.value.append(_geometry)

		
		
