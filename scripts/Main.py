
from pymjin2 import *

import random

MAIN_LCD_NAME       = "lcd"
MAIN_SOUND_START    = "soundBuffer.default.start"
MAIN_TILE_MOVE_UP   = "move.default.liftTile"
MAIN_TILE_MOVE_DOWN = "move.default.lowerTile"

class MainImpl(object):
    def __init__(self, c):
        self.c = c
        self.isStarted = False
    def __del__(self):
        self.c = None
    def onSpace(self, key, value):
        print "Space pressed"
        if (self.isStarted):
            print "The game has already been started"
            return
        self.isStarted = True
        self.c.set("esequence.default.start.active", "1")
    def setAssignFilterTileToDestination(self, key, value):
        tileName = self.c.get("filter.lastUsedTile")[0]
        self.c.set("filter.removeUsedTile", "1")
        self.c.set("destination.acceptTile", tileName)
        self.c.report("main.assignFilterTileToDestination", "0")
    def setAssignSelectedDestinationTileToFilter(self, key, value):
        print "01.assign dst->flt"
        tileName = self.c.get("destination.lastSelectedTile")[0]
        print "02.assign dst->flt"
        self.c.set("destination.removeSelectedTile", "1")
        print "03.assign dst->flt"
        self.c.set("filter.acceptTile", tileName)
        print "04.assign dst->flt"
        self.c.report("main.assignSelectedDestinationTileToFilter", "0")
        print "05.assign dst->flt"
    def setAssignSelectedSourceTileToFilter(self, key, value):
        tileName = self.c.get("source.lastSelectedTile")[0]
        self.c.set("source.removeSelectedTile", "1")
        self.c.set("filter.acceptTile", tileName)
        self.c.report("main.assignSelectedSourceTileToFilter", "0")
    def setClearLCD(self, key, value):
        self.c.set("lcd.$SCENE.$LCD.value", "")
        self.c.report("main.clearLCD", "0")
    def setProvideRandomLCDValue(self, key, value):
        random.seed()
        i = random.randint(0, 9999)
        self.c.set("lcd.$SCENE.$LCD.value", str(i))
        self.c.report("main.provideRandomLCDValue", "0")
    # replayStartSound.
    def setReplayStartSound(self, key, value):
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

        self.c.provide("main.assignFilterTileToDestination",
                       self.impl.setAssignFilterTileToDestination)
        self.c.provide("main.assignSelectedDestinationTileToFilter",
                       self.impl.setAssignSelectedDestinationTileToFilter)
        self.c.provide("main.assignSelectedSourceTileToFilter",
                       self.impl.setAssignSelectedSourceTileToFilter)
        self.c.provide("main.clearLCD",         self.impl.setClearLCD)
        self.c.provide("main.provideRandomLCDValue", self.impl.setProvideRandomLCDValue)
        self.c.provide("main.replayStartSound", self.impl.setReplayStartSound)

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
            # Process items.
            items = []
            for item in v:
                # Environment API call.
                if ("." in item):
                    pass
                # Another sequence.
                else:
                    item = "esequence.default.{0}.active".format(item)
                items.append(item)
            self.c.set("esequence.default.$NAME.sequence", items)

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

