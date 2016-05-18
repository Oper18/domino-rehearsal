
from pymjin2 import *

DESTINATION_ACTION_LIFT_TILE   = "move.default.liftTile"
DESTINATION_ACTION_ROTATE      = "rotate.default.rotateDestination"
DESTINATION_LEAF_PREFIX        = "destinationLeaf"
DESTINATION_SEQUENCE_SELECTION = "esequence.default.destinationTileSelection"
DESTINATION_SLOTS_NB           = 10

class DestinationImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = {}
        for i in xrange(0, DESTINATION_SLOTS_NB):
            self.tiles[i] = None
        self.lastAcceptedTile = None
        self.lastSelectedTile = None
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
    # isFull.
    def getIsFull(self, key):
        full = True
        for slot, tile in self.tiles.items():
            if (tile is None):
                full = False
                break
        return ["1" if full else "0"]
    # lastSelectedTile.
    def getLastSelectedTile(self, key):
        return [self.lastSelectedTile]
    # result.
    def getResult(self, key):
        res = 0
        for slot, tile in self.tiles.items():
            self.c.setConst("TILE", tile)
            mat = self.c.get("node.$SCENE.$TILE.material")[0]
            v0 = int(mat[-2])
            v1 = int(mat[-1])
            res = res + v0 + v1
        return [str(res)]
    # alignFreeSlotWithFilter.
    def onAlignFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("destination.alignFreeSlotWithFilter", "0")
    # alignSelectedTileWithFilter.
    def onAlignSelFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("destination.alignSelectedTileWithFilter", "0")
    # liftLastAcceptedTile.
    def onTileLifted(self, key, value):
        self.c.unlisten("$LIFT.$SCENE.$TILE.active")
        self.c.report("destination.liftLastAcceptedTile", "0")
    def onTileSelection(self, key, value):
        self.lastSelectedTile = key[2]
        self.c.setConst("SEQ", DESTINATION_SEQUENCE_SELECTION)
        self.c.set("$SEQ.active", "1")
    def prepareTargetRotation(self, slotID):
        # Set new rotation.
        r = 90 - 36 * slotID
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
        self.prepareTargetRotation(self.lastFreeSlotID)
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.onAlignFinish)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
    # alignSelectedTileWithFilter.
    def setAlignSelectedTileWithFilter(self, key, value):
        # Find selected slot.
        slotID = None
        for slot, tile in self.tiles.items():
            if (tile == self.lastSelectedTile):
                slotID = slot
                break
        self.prepareTargetRotation(slotID)
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.onAlignSelFinish)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
    # allowTileSelection.
    def setAllowTileSelection(self, key, value):
        for slot, tile in self.tiles.items():
            if (tile is not None):
                self.c.setConst("TILE", tile)
                self.c.listen("node.$SCENE.$TILE.selected",
                              "1",
                              self.onTileSelection)
        self.c.report("destination.allowTileSelection", "0")
    # disallowTileSelection.
    def setDisallowTileSelection(self, key, value):
        for slot, tile in self.tiles.items():
            if (tile is not None):
                self.c.setConst("TILE", tile)
                self.c.unlisten("node.$SCENE.$TILE.selected")
        self.c.report("destination.disallowTileSelection", "0")
    # liftLastAcceptedTile.
    def setLiftLastAcceptedTile(self, key, value):
        self.c.setConst("LIFT", DESTINATION_ACTION_LIFT_TILE)
        self.c.listen("$LIFT.$SCENE.$TILE.active", "0", self.onTileLifted)
        self.c.set("$LIFT.$SCENE.$TILE.active", "1")
    # removeSelectedTile.
    def setRemoveSelectedTile(self, key, value):
        for slot, tile in self.tiles.items():
            if (tile == self.lastSelectedTile):
                self.tiles[slot] = None
                self.lastSelectedTile = None
                break

class Destination(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Destination")
        self.impl = DestinationImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("destination.acceptTile", self.impl.setAcceptTile)
        self.c.provide("destination.alignFreeSlotWithFilter",
                       self.impl.setAlignFreeSlotWithFilter)
        self.c.provide("destination.alignSelectedTileWithFilter",
                       self.impl.setAlignSelectedTileWithFilter)
        self.c.provide("destination.allowTileSelection",
                       self.impl.setAllowTileSelection)
        self.c.provide("destination.disallowTileSelection",
                       self.impl.setDisallowTileSelection)
        self.c.provide("destionation.isFull", None, self.impl.getIsFull)
        self.c.provide("destination.lastSelectedTile",
                       None,
                       self.impl.getLastSelectedTile)
        self.c.provide("destination.liftLastAcceptedTile",
                       self.impl.setLiftLastAcceptedTile)
        self.c.provide("destination.removeSelectedTile",
                       self.impl.setRemoveSelectedTile)
        self.c.provide("destination.result", None, self.impl.getResult)
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

