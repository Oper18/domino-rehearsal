
from pymjin2 import *

import random

MAIN_LCD_NAME       = "lcd"
MAIN_SOUND_START    = "soundBuffer.default.start"
MAIN_TILE_MOVE_UP   = "move.default.liftTile"
MAIN_TILE_MOVE_DOWN = "move.default.lowerTile"

class MainImpl(object):
    def __init__(self, c):
        self.c = c
    def __del__(self):
        self.c = None
    def onSpace(self, key, value):
        print "Space pressed. Run start sequence"
        self.c.set("esequence.default.start.active", "1")
    def setClearLCD(self, key, value):
        self.c.set("lcd.$SCENE.$LCD.value", "")
        self.c.report("main.clearLCD", "0")
    def setProvideRandomLCDValue(self, key, value):
        random.seed()
        i = random.randint(0, 9999)
        self.c.set("lcd.$SCENE.$LCD.value", str(i))
        self.c.report("main.provideRandomLCDValue", "0")
    # moveTileDown.
    def onMoveTileDownFinish(self, key, value):
        print "onMoveTileDownFinish", key, value
        self.c.unlisten("$MOVE_TILE_DOWN.$SCENE.$NODE.active")
        self.c.report("main.moveTileDown", "0")
    def setMoveTileDown(self, key, value):
        print "setMoveTileDown", key, value
        # Only accept activation value.
        if (value[0] != "1"):
            return
        # Subscribe to the action finish.
        self.c.setConst("MOVE_TILE_DOWN", MAIN_TILE_MOVE_DOWN)
        self.c.setConst("NODE", "tile")
        self.c.listen("$MOVE_TILE_DOWN.$SCENE.$NODE.active", "0", self.onMoveTileDownFinish)
        # Activate action.
        self.c.set("$MOVE_TILE_DOWN.$SCENE.$NODE.active", "1")
    # moveTileUp.
    def onMoveTileUpFinish(self, key, value):
        print "onMoveTileUpFinish", key, value
        self.c.unlisten("$MOVE_TILE_UP.$SCENE.$NODE.active")
        self.c.report("main.moveTileUp", "0")
    def setMoveTileUp(self, key, value):
        print "setMoveTileUp", key, value
        # Only accept activation value.
        if (value[0] != "1"):
            return
        # Subscribe to the action finish.
        self.c.setConst("MOVE_TILE_UP", MAIN_TILE_MOVE_UP)
        self.c.setConst("NODE", "tile")
        self.c.listen("$MOVE_TILE_UP.$SCENE.$NODE.active", "0", self.onMoveTileUpFinish)
        # Activate action.
        self.c.set("$MOVE_TILE_UP.$SCENE.$NODE.active", "1")
    # replayStartSound.
    def setReplayStartSound(self, key, value):
        print "setReplayStartSound", key, value
        self.c.setConst("SNDSTART", MAIN_SOUND_START)
        self.c.set("$SNDSTART.state", "play")
        # We don't wait for its completion for simplicity.
        self.c.report("main.replayStartSound", "0")

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        self.c.setConst("SCENE",    sceneName)
        self.c.setConst("LCD",      MAIN_LCD_NAME)
        self.c.listen("input.SPACE.key", "1", self.impl.onSpace)

        # Sequences test. Provide global game API.
        # moveTileUp.
        self.c.provide("main.moveTileUp",       self.impl.setMoveTileUp)
        # moveTileDown.
        self.c.provide("main.moveTileDown",     self.impl.setMoveTileDown)
        # replayStartSound.
        self.c.provide("main.replayStartSound", self.impl.setReplayStartSound)
        self.c.provide("main.provideRandomLCDValue", self.impl.setProvideRandomLCDValue)
        self.c.provide("main.clearLCD",         self.impl.setClearLCD)

        # Read sequence file.
        # TODO: Move to ESequence. Make it prettier.
        lns = None
        self.c.setConst("FILENAME", "scripts/sequences")
        fileName = self.c.get("pathResolver.$FILENAME.absoluteFileName")[0]
        with open(fileName, "r") as f:
            lns = f.readlines()
        # Parse the file.
        self.c.setConst("ESEQGROUP", "default")
        seqs = {}
        lastSeqName = None
        for ln in lns:
            # Sequence name.
            if (ln[0].isalpha()):
                lastSeqName = ln.strip()
                seqs[lastSeqName] = []
            # Sequence item.
            else:
                seqs[lastSeqName].append(ln.strip())
        # Create sequences.
        for k, v in seqs.items():
            self.c.setConst("NAME", k)
            self.c.set("esequence.default.$NAME.sequence", v)
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

