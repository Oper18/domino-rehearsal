
from pymjin2 import *

DESTINATION_ACTION_LIFT_TILE = "move.default.liftTile"
DESTINATION_ACTION_ROTATE    = "rotate.default.rotateDestination"
DESTINATION_LEAF_PREFIX      = "destinationLeaf"
DESTINATION_SLOTS_NB         = 10

class DestinationImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = {}
        for i in xrange(0, DESTINATION_SLOTS_NB):
            self.tiles[i] = None
        self.lastAcceptedTile = None
        self.lastFreeSlotID = None
        self.rotationSpeed = None
    def __del__(self):
        self.c = None
    def findFreeSlot(self):
        self.lastFreeSlotID = None
        for slot, tile in self.tiles.items():
            if (tile is None):
                self.lastFreeSlotID = slot
                break
    # alignFreeSlotWithFilter.
    def onAlignFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("destination.alignFreeSlotWithFilter", "0")
    # liftLastAcceptedTile.
    def onTileLifted(self, key, value):
        self.c.unlisten("$LIFT.$SCENE.$TILE.active")
        self.c.report("destination.liftLastAcceptedTile", "0")
    def prepareTargetRotation(self):
        # Set new rotation.
        r = 90 - 36 * self.lastFreeSlotID
        self.c.set("$ROTATE.point",
                   "{0} 0 0 {1}".format(self.rotationSpeed, r))
    def recordRotationSpeedOnce(self):
        if (self.rotationSpeed is not None):
            return
        self.c.setConst("ROTATE", DESTINATION_ACTION_ROTATE)
        p = self.c.get("$ROTATE.point")[0]
        self.rotationSpeed = p.split(" ")[0]
    # acceptTile.
    def setAcceptTile(self, key, value):
        self.lastAcceptedTile = value[0]
        self.tiles[self.lastFreeSlotID] = self.lastAcceptedTile
        freeLeaf = DESTINATION_LEAF_PREFIX + str(self.lastFreeSlotID)
        self.c.setConst("TILE", self.lastAcceptedTile)
        self.c.set("node.$SCENE.$TILE.parentAbs", freeLeaf)
    # alignFreeSlotWithFilter.
    def setAlignFreeSlotWithFilter(self, key, value):
        self.recordRotationSpeedOnce()
        self.findFreeSlot()
        self.prepareTargetRotation()
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.onAlignFinish)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
    # liftLastAcceptedTile.
    def setLiftLastAcceptedTile(self, key, value):
        self.c.setConst("LIFT", DESTINATION_ACTION_LIFT_TILE)
        self.c.listen("$LIFT.$SCENE.$TILE.active", "0", self.onTileLifted)
        self.c.set("$LIFT.$SCENE.$TILE.active", "1")

class Destination(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Destination")
        self.impl = DestinationImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("destination.acceptTile", self.impl.setAcceptTile)
        self.c.provide("destination.alignFreeSlotWithFilter",
                       self.impl.setAlignFreeSlotWithFilter)
        self.c.provide("destination.liftLastAcceptedTile",
                       self.impl.setLiftLastAcceptedTile)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Destination(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

