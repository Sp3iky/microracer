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
import time

from avango.script import field_has_changed

# import modules from local library
from lib.globals import *


class SixDofInputDevice(avango.script.Script):
      
    # output fields
    dof_out = avango.MFFloat()
    dof_out.value = [0.0,0.0,0.0,0.0,0.0,0.0] # init six channels

    button1_out = avango.SFBool()
    button2_out = avango.SFBool()
       
    # constructor
    def __init__(self):
        self.super(SixDofInputDevice).__init__()

        # sensor
        self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())

        # field connections
        self.button1_out.connect_from(self.device_sensor.Button0)
        self.button2_out.connect_from(self.device_sensor.Button1)

        # variables
        self.time_sav = time.time()
        
        self.always_evaluate(True) # activate evaluate callback
        
    # functions
    def filter_channel(self, VALUE, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD):
        VALUE = VALUE - OFFSET
        MIN = MIN - OFFSET
        MAX = MAX - OFFSET

        if VALUE > 0:
            _pos = MAX * POS_THRESHOLD * 0.01
            if VALUE > _pos: # above positive threshold
                VALUE = min( (VALUE - _pos) / (MAX - _pos), 1) # normalize interval
            else: # beneath positive threshold
                VALUE = 0       

        elif VALUE < 0:
            _neg = MIN * NEG_THRESHOLD * 0.01
            if VALUE < -_neg:
                VALUE = max( ((VALUE + _neg) / (MIN + _neg)) * -1, -1)
            else: # beneath negative threshold
                VALUE = 0

        return VALUE
        
    


class SpacemouseDevice(SixDofInputDevice):

    # constructor
    def __init__(self):
        self.super(SpacemouseDevice).__init__()

        # sensor    
        self.device_sensor.Station.value = "device-spacemouse"

    # callbacks
    def evaluate(self):

        _fr_scale_factor = 60 / (1 / (time.time() - self.time_sav)) # frame rate scale factor
        self.time_sav = time.time()
        
        # translation
        _x = self.filter_channel(self.device_sensor.Value0.value, 0, -0.83, 0.86, 10, 10)
        _y = self.filter_channel(self.device_sensor.Value2.value, 0, -0.86, 0.92, 10, 10)
        _z = self.filter_channel(self.device_sensor.Value1.value, 0, -0.95, 0.90, 10, 10)
        #print "x,y,z : ", _x, _y, _z
        
        # rotation
        _rx = self.filter_channel(self.device_sensor.Value3.value, 0, -0.75, 0.8, 25, 25) # pitch
        _ry = self.filter_channel(self.device_sensor.Value5.value, 0, -0.65, 0.68, 25, 25) # head
        _rz = self.filter_channel(self.device_sensor.Value4.value, 0, -0.72, 0.84, 25, 25) # roll

        # forward data --> multi field connection
        self.dof_out.value[0] = _x * _fr_scale_factor
        self.dof_out.value[1] = _y * _fr_scale_factor * -1.0
        self.dof_out.value[2] = _z * _fr_scale_factor
        self.dof_out.value[3] = _rx * _fr_scale_factor
        self.dof_out.value[4] = _ry * _fr_scale_factor * -1.0
        self.dof_out.value[5] = _rz * _fr_scale_factor
        
class Navigation(avango.script.Script):

    # input fields
    dof_in = avango.MFFloat()

    # output fields
    mat_out = avango.osg.SFMatrix()
    
    maneuver_direction = avango.osg.Vec3()
    translation_length = 0.0
    accumulated_rotation_vector = avango.osg.Vec3()
    camera_rotation = avango.osg.make_ident_mat()
    pick_to_camera_offset = avango.osg.Vec3()
    pick_position = avango.osg.Vec3()
    
    # constructor
    def __init__(self):
        self.super(Navigation).__init__()
                
        # parameters
        self.transition_duration = 4.0 # sec
                
        # variables        
        self.transition_start_mat = avango.osg.make_ident_mat()
        self.transition_end_mat = avango.osg.make_ident_mat()
        self.transition_start_time = 0.0
        
        self.navigation_mode = 0 # 0 = steering-based navigation; 1 = viewpoint maneuvering; 2 target-based navigation; 3 animation sequence
        self.reference_point = avango.osg.Vec3()
        
    def my_constructor(self, SCENE, VIEWING_SETUP, INPUT_DEVICE):

        # references
        self.SCENE = SCENE

        self.mat_out.value = SCENE.navigation_transform.Matrix.value # initial navigation values

        # init field connections    
        self.dof_in.connect_from(INPUT_DEVICE.dof_out)
        
        SCENE.navigation_transform.Matrix.connect_from(self.mat_out)

        # init further device sensors
        self.keyboard_sensor = avango.daemon.nodes.DeviceSensor(Station = "device-keyboard", DeviceService = gl_device_service)
        self.mouse_sensor = avango.daemon.nodes.DeviceSensor(Station = "device-mouse", DeviceService = gl_device_service)

        # - pick selector performs object intersection check with every geometry nodes reachable in a specified subgraph
        # - RootNode field specifies entry point for intersection check
        # - PickTrigger (SFBool) field enables/disables intersection check
        # - PickRayTransform (SFMatrix) field defines position and orientation of the intersection start point
        # - PickRayLength (SFFloat) field defines length of the intersection ray
        # - if intersection is found the target is provided by the field SelectedTargets        

        # pick selector for definition of reference point
        self.pick_selector1 = avango.tools.nodes.PickSelector(TransitionOnly = True, RootNode = SCENE.root, CreateIntersections = True)
        self.pick_selector1.PickTrigger.connect_from(self.mouse_sensor.Button0)
        self.pick_selector1.PickRayTransform.connect_from(VIEWING_SETUP.setup.camera.MouseNearTransform)

        # pick selector for camera avatar adjustment in target-based navigation mode
        self.pick_selector2 = avango.tools.nodes.PickSelector(TransitionOnly = False, RootNode = SCENE.object_root, CreateIntersections = True)
        self.pick_selector2.PickTrigger.connect_from(self.mouse_sensor.Button1)
        self.pick_selector2.PickRayTransform.connect_from(VIEWING_SETUP.setup.camera.MouseNearTransform)
        
        # reference point geometry
        self.intersection_geometry = avango.osg.nodes.LoadFile(Filename = 'data/sphere.obj')

        self.intersection_transform = avango.osg.nodes.MatrixTransform()
        SCENE.interface_root.Children.value.append(self.intersection_transform)
        
        # ray geometry for target-based navigation
        self.ray_geometry = avango.osg.nodes.LoadFile(Filename = 'data/cylinder.obj')
        self.ray_geometry.add_field(avango.SFUInt(), "PickMask") # disable object for intersection
    
        self.ray_transform = avango.osg.nodes.MatrixTransform()
        SCENE.interface_root.Children.value.append(self.ray_transform)
        
        # camera geometry for target-based navigation
        self.camera_geometry = avango.osg.nodes.LoadFile(Filename = 'data/cam_blue.iv', Matrix = avango.osg.make_scale_mat(3.0,3.0,3.0) * avango.osg.make_rot_mat(math.pi,1,0,0) * avango.osg.make_trans_mat(0.0,0.0,0.15))
        self.camera_geometry.add_field(avango.SFUInt(), "PickMask") # disable object for intersection
    
        self.camera_transform = avango.osg.nodes.MatrixTransform()
        SCENE.interface_root.Children.value.append(self.camera_transform)
        
        # mode visualization nodes
        self.panel = avango.osg.nodes.Panel(PanelColor = avango.osg.Vec4(0.5,0.5,0.5,0.5), Width = 0.08, Height = 0.04, BorderWidth = 0.005)
        self.panel.Position.value = avango.osg.Vec3(gl_physical_screen_width * 0.35, gl_physical_screen_height * 0.35, 0.0)
        self.panel.EdgeSmooth.value = 1
        
        self.text = avango.osg.nodes.Text(Size = 0.01, Alignment = 4, Fontname = "VeraBI.ttf", Color = avango.osg.Vec4(1.0,0.0,0.0,1.0))
        self.text.Position.value = avango.osg.Vec3(gl_physical_screen_width * 0.35, gl_physical_screen_height * 0.35, 0.0)

        self.geode = avango.osg.nodes.LayerGeode(Drawables = [self.panel, self.text], StateSet = avango.osg.nodes.StateSet(LightingMode = 0))
        SCENE.navigation_transform.Children.value.append(self.geode) # append gui to navigation node --> head up display
        
    # callbacks
    def evaluate(self):
    
        self.update_picking_setup()    
        self.trigger_camera_to_ground_allignment()
        self.navigate()
        self.update_mode_visualization()
    
    def translation_transfer_function(self, value):
        threshold = 0.3
        sign = 1.0
        if value != 0.0:
            sign = value / math.fabs(value)
    
        if math.fabs(value) < threshold:
            return 0.0
        else:
            return sign * 0.3 * math.pow(math.fabs(value) - threshold, 2.0)
    
    def rotation_transfer_function(self, value):
        threshold = 0.15
        sign = 1.0
        if value != 0.0:
            sign = value / math.fabs(value)
    
        if math.fabs(value) < threshold:
            return 0.0
        else:
            return sign * 0.03 * math.pow(math.fabs(value) - threshold, 2.0)
        
    # functions
    def navigate(self):
        # translations
        _x = self.translation_transfer_function(self.dof_in.value[0])
        _y = self.translation_transfer_function(self.dof_in.value[1])
        _z = self.translation_transfer_function(self.dof_in.value[2])
        
        # rotations
        _pitch = self.rotation_transfer_function(self.dof_in.value[3])
        _head  = self.rotation_transfer_function(self.dof_in.value[4])  
        _roll  = self.rotation_transfer_function(self.dof_in.value[5])
        
        if self.navigation_mode == 0: # steering mode
            
            translation_matrix = avango.osg.make_trans_mat(_x, _y, _z)
            
            head_rotation_matrix = avango.osg.make_rot_mat(_head, 0.0, 1.0, 0.0)
            pitch_rotation_matrix = avango.osg.make_rot_mat(_pitch, 1.0, 0.0, 0.0)
            roll_rotation_matrix = avango.osg.make_rot_mat(_roll, 0.0, 0.0, 1.0)
            
            new_matrix = translation_matrix * head_rotation_matrix * pitch_rotation_matrix * roll_rotation_matrix
            self.mat_out.value = new_matrix * self.mat_out.value
            
        elif self.navigation_mode == 1: # viewpoint maneuvering mode
            
            # only change in z-direction needed for zoom to the point
            self.translation_length += _z
            
            # rotation change
            inverse_point = avango.osg.Vec3(-self.reference_point.x, -self.reference_point.y, -self.reference_point.z)
            rotation_change_vector = avango.osg.Vec3(_pitch, _head, _roll)
            self.accumulated_rotation_vector += rotation_change_vector
            new_rotation = rotation_change_vector * self.SCENE.navigation_transform.Matrix.value.get_rotate()
            
            # (1) move into the point 
            # (2) rotate around the point 
            # (3) move back to camera position
            rotation_x_matrix = avango.osg.make_trans_mat(inverse_point) *\
                avango.osg.make_rot_mat(new_rotation.x, 1.0, 0.0, 0.0) *\
                avango.osg.make_trans_mat(self.reference_point)
            rotation_y_matrix = avango.osg.make_trans_mat(inverse_point) *\
                avango.osg.make_rot_mat(new_rotation.y, 0.0, 1.0, 0.0) *\
                avango.osg.make_trans_mat(self.reference_point)
            rotation_z_matrix = avango.osg.make_trans_mat(inverse_point) *\
                avango.osg.make_rot_mat(new_rotation.z, 0.0, 0.0, 1.0) *\
                avango.osg.make_trans_mat(self.reference_point)
            
            # (1) translate along the maneuver-direction vector
            # (2) and translate to the camera offset
            trans_direction = self.pick_selector1.PickRayTransform.value.get_translate() - self.reference_point
            
            trans_direction.normalize()
            
            translation_matrix = avango.osg.make_trans_mat(trans_direction * _z)
            self.mat_out.value *= rotation_x_matrix * rotation_y_matrix * rotation_z_matrix * translation_matrix  
            
        elif self.navigation_mode == 3: # animation sequence

            _time_step = time.time() - self.transition_start_time

            _start_pos = self.transition_start_mat.get_translate()
            _target_pos = self.transition_end_mat.get_translate()

            if _time_step >= self.transition_duration: # animation sequence finished

                self.navigation_mode = 0 # disable transition sequence --> switch back to steering mode

                self.mat_out.value = self.transition_end_mat # snap to exact target position & orientation

            else: # active animation sequence
                _factor = _time_step / self.transition_duration # actual animation step normalized [0,1]
            
                # animate orientation with spherical linear interpolation (SLERP)
                _quat = avango.osg.Quat()    
                _quat.slerp(_factor, self.transition_start_mat.get_rotate(),  self.transition_end_mat.get_rotate()) # slerp parameters: factor [0,1]; start quaternion (rotation); target quaternion (rotation)
            
                # animate position
                _vec = _target_pos - _start_pos
                _vec = _start_pos + _vec * _factor

                # apply animation input to navigation matrix
                self.mat_out.value =     avango.osg.make_rot_mat(_quat) * \
                                        avango.osg.make_trans_mat(_vec)



    def update_picking_setup(self):
        
        if len(self.pick_selector1.SelectedTargets.value) > 0 or len(self.pick_selector2.SelectedTargets.value) > 0: # targets found
            # task 2
            if len(self.pick_selector1.SelectedTargets.value) > 0: # targets found
                
                self.intersection_transform.Children.value = [self.intersection_geometry] # enable intersection point visualization

                _point = self.pick_selector1.SelectedTargets.value[0].Intersection.value.Point.value # get the intersection point wth the object geometry (in world coordinates)
                
                self.intersection_transform.Matrix.value = avango.osg.make_scale_mat(0.05,0.05,0.05) * avango.osg.make_trans_mat(_point) # update reference point visualization
                self.reference_point = _point # save the intersection point --> used as rotation center in viewpoint maneuvering mode
                
                if self.navigation_mode != 1:
                    self.navigation_mode = 1 # switch to viewpoint maneuvering mode
                    
                    # determine maneuver direction
                    self.pick_position = self.pick_selector1.PickRayTransform.value.get_translate()
                    self.maneuver_direction = self.pick_position - _point
                    self.translation_length = self.maneuver_direction.length()
                    self.pick_to_camera_offset = self.mat_out.value.get_translate() - self.pick_position
                    self.maneuver_direction.normalize()
                    
                    # reset accumulation matrices
                    rotation_vector = avango.osg.Vec3()
                    self.camera_rotation = avango.osg.make_rot_mat(self.mat_out.value.get_rotate())
                    
            elif len(self.pick_selector2.SelectedTargets.value) > 0: # targets found
                # task 3
                if self.navigation_mode == 0:
                    
                    self.navigation_mode = 2 # switch to target-based navigation mode

                    self.intersection_transform.Children.value = [self.intersection_geometry] # enable intersection point visualization
                    self.ray_transform.Children.value = [self.ray_geometry] # enable ray visualization
                    self.camera_transform.Children.value = [self.camera_geometry] # enable camera visualization

                    # update target point visualization
                    _point = self.pick_selector2.SelectedTargets.value[0].Intersection.value.Point.value # get the intersection point wth the object geometry (in world coordinates)
                    self.intersection_transform.Matrix.value = avango.osg.make_scale_mat(0.35) * avango.osg.make_trans_mat(_point) # update reference target-based navigation sphere visualization
                    
                    self.pick_selector2.RootNode.value = self.SCENE.interface_root # pick selector should intersect only with target-based navigation sphere --> other scene objects are excluded for intersection
                    
                
                elif self.navigation_mode == 2:

                    # update target-based navigation visualizations
                    _point1 = self.pick_selector2.SelectedTargets.value[0].Intersection.value.Point.value # intersection point with target-based navigation sphere
                    _point2 = self.intersection_transform.Matrix.value.get_translate() # target-based navigation sphere center --> reference point
        
                    _diff = _point1 - _point2
                    _length = _diff.length()
                    _diff.normalize()
                    _ref = avango.osg.Vec3(0.0,0.0,1.0) # reference direction
                    _mat = avango.osg.make_rot_mat(math.acos(_ref * _diff), _ref ^ _diff)
        
                    # update ray visualization
                    self.ray_transform.Matrix.value =     avango.osg.make_scale_mat(0.02, 0.02, _length * 2.0) * \
                                                        _mat * \
                                                        avango.osg.make_trans_mat(_point1)
        
                    # update camera avatar visualization
                    self.camera_transform.Matrix.value =     _mat * \
                                                            avango.osg.make_trans_mat(_point1 + _diff * 0.35)
        


        else: # no targets found

            if self.navigation_mode == 1: # maneuvering
    
                self.intersection_transform.Children.value = [] # disable intersection point visualization

                self.navigation_mode = 0 # switch to steering mode

            elif self.navigation_mode == 2 and self.mouse_sensor.Button1.value == False: # target-based navigation

                # do something usefull here
                self.trigger_camera_to_avatar_transition()
                
                self.pick_selector2.RootNode.value = self.SCENE.object_root # pick selector intersects with all scene objects
                
                self.intersection_transform.Children.value = [] # disable intersection point visualization
                self.ray_transform.Children.value = [] # disable ray visualization
                self.camera_transform.Children.value = [] # disable camera visualization    

    
    def trigger_camera_to_ground_allignment(self):

        if self.keyboard_sensor.Button5.value == True and self.navigation_mode != 3: # trigger ground alignment animation

            self.transition_start_mat = self.mat_out.value # start matrix of camera transition

            _start_pos = self.transition_start_mat.get_translate()
            _target_pos = avango.osg.Vec3(_start_pos.x, 1.2, _start_pos.z) # set target position height to fixed value

            _head = self.get_euler_angles(self.mat_out.value) # only head rotation value required for new camera orientation (pitch & roll rotation ignored)
            
            self.transition_end_mat =     avango.osg.make_rot_mat(_head, 0, 1, 0) * \
                                        avango.osg.make_trans_mat(_target_pos)

            self.transition_start_time = time.time()
            
            self.navigation_mode = 3 # switch to animation mode
    
    def trigger_camera_to_avatar_transition(self):
        
        if self.navigation_mode != 3: # trigger ground alignment animation
            
            self.transition_start_mat = self.mat_out.value # start matrix of camera transition

            _start_pos = self.transition_start_mat.get_translate()
            _target_pos = avango.osg.Vec3(_start_pos.x, 1.2, _start_pos.z) # set target position height to fixed value
            
            _head = self.get_euler_angles(self.mat_out.value) # only head rotation value required for new camera orientation (pitch & roll rotation ignored)
            
            self.transition_end_mat = self.camera_transform.Matrix.value     
            # avango.osg.make_rot_mat(_head, 0, 1, 0) * \
            # avango.osg.make_trans_mat(_target_pos)
            
            self.transition_start_time = time.time()
            
            self.navigation_mode = 3 # switch to animation mode
            
    def update_mode_visualization(self):

        if self.navigation_mode == 0: # steering 
            self.text.String.value = "Steering"

        elif self.navigation_mode == 1: # maneuvering
            self.text.String.value = "Maneuvering"
        
        elif self.navigation_mode == 2: # target-based navigation
            self.text.String.value = "Target-based"

        elif self.navigation_mode == 3: # animation sequence
            self.text.String.value = "Animation"
            


    def get_euler_angles(self, MATRIX):

        quat = MATRIX.get_rotate()
        qx = quat.x
        qy = quat.y
        qz = quat.z
        qw = quat.w
        
        sqx = qx * qx
        sqy = qy * qy
        sqz = qz * qz
        sqw = qw * qw

        unit = sqx + sqy + sqz + sqw # if normalised is one, otherwise is correction factor
        test = (qx * qy) + (qz * qw)


        if test > (0.49999 * unit): # singularity at north pole
            head = 2 * math.atan2(qx,qw)
            roll = math.pi/2
            pitch = 0
        elif test < (-0.49999 * unit): # singularity at south pole
            head = -2 * math.atan2(qx,qw)
            roll = math.pi/-2
            pitch = 0
        else:
            head = math.atan2(2 * qy * qw - 2 * qx * qz, 1 - 2 * sqy - 2 * sqz)
            roll = math.asin(2 * test)
            pitch = math.atan2(2 * qx * qw - 2 * qy * qz, 1 - 2 * sqx - 2 * sqz)

            if head < 0:
                head += 2 * math.pi
            '''
            #if pitch < 0:
            #    pitch += 2 * math.pi
            if roll < 0:
                roll += 2 * math.pi
            '''

        return head
    
