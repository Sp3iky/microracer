# ----------------------------------------------------------------
# MicroRacer GameLogic Class
# - Starts and finishes a race
# - Start/Finish detection
# - Triggers/Watches for checkpoints
# - Time and lap counter
# ----------------------------------------------------------------

import avango
import avango.osg
import time

from avango.script import field_has_changed

# import modules from local library
from lib.globals import *

class GameLogic(avango.script.Script):
      
    # members
    
    # constructor
    def __init__(self):
        self.super(GameLogic).__init__()
        
