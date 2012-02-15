# ----------------------------------------------------------------
# MicroRacer HUD Class
# - Draws the hud for a player
# ----------------------------------------------------------------

import avango
import avango.osg
import time

from avango.script import field_has_changed

# import modules from local library
from lib.globals import *

class HUD(avango.script.Script):
      
    # members
    
    # constructor
    def __init__(self):
        self.super(HUD).__init__()
        
