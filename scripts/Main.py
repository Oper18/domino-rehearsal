
from pymjin2 import *

MAIN_LCD_NAME       = "lcd"
MAIN_SOUND_START    = "soundBuffer.default.start"

class MainImpl(object):
    def __init__(self, c):
        self.c = c
    def __del__(self):
        self.c = None
    def onSpace(self, key, value):
        print "Space pressed."
        self.c.set("$SNDSTART.state", "play")
        # Set LCD value.
        self.c.set("lcd.$SCENE.$LCD.value", "273")
    def setMoveTileDown(self, key, value):
        print "setMoveTileDown", key, value
        # TODO - / - / -.
    # moveTileUp.
    def onMoveTileUpFinish(self, key, value):
        print "onMoveTileUpFinish", key, value
        self.c.unlisten("$MOVE_TILE_UP.active")
        self.c.report
    def setMoveTileUp(self, key, value):
        print "setMoveTileUp", key, value
        # Only accept activation value.
        if (value[0] != "1"):
            return
        # Subscribe to the action finish.
        # TODO: How to provide? 
        self.c.setConst("MOVE_TILE_UP", "default.move.liftTile")
        self.c.listen("$MOVE_TILE_UP.active", "0", self.onMoveTileUpFinish)
        # Activate action.
        # TODO: How to provide?
        self.c.setConst("NODE", "tile")
        self.c.set("$MOVE_TILE_UP.$SCENE.$NODE.active", "1")

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        self.c.setConst("SCENE",    sceneName)
        self.c.setConst("LCD",      MAIN_LCD_NAME)
        self.c.setConst("SNDSTART", MAIN_SOUND_START)
        self.c.listen("input.SPACE.key", "1", self.impl.onSpace)

        # Sequences test. Provide global game API.
        # moveTileUp.
        self.c.provide("moveTileUp",       self.impl.setMoveTileUp)
        self.c.provide("moveTileDown",     self.impl.setMoveTileDown)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Main(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

