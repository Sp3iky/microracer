# ----------------------------------------------------------------
# MicroRacer Player Class
# - Controls one player
# ----------------------------------------------------------------

import avango
import avango.osg
import time

from avango.script import field_has_changed

# import modules from local library
from lib.globals import *

class Player(avango.script.Script):
      
    # members
    
    # constructor
    def __init__(self):
        self.super(Player).__init__()
        
