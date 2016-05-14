
from pymjin2 import *

FILTER_ACTION_DROP_ACCEPTED_TILE = "move.default.dropFilterTile"
FILTER_ACTION_DROP_NEW_TILE      = "move.default.lowerTile"
FILTER_ACTION_ROTATE             = "rotate.default.rotateFilter"
FILTER_LEAF_FILTER_ID            = 0
FILTER_LEAF_PREFIX               = "filterLeaf"
FILTER_SLOTS_NB                  = 3
FILTER_TILE_INITIAL_POS          = "0 0 11"

class FilterImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = {}
        for i in xrange(0, FILTER_SLOTS_NB):
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
    # dropLastAcceptedTile.
    def onAcceptedTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("filter.dropLastAcceptedTile", "0")
    # alignFreeSlotWithSource.
    def onAlignFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("filter.alignFreeSlotWithSource", "0")
    # dropLastCreatedTile.
    def onTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("filter.dropLastCreatedTile", "0")
    def prepareTargetRotation(self):
        # Set new rotation.
        r = 90 - 120 * self.lastFreeSlotID
        self.c.set("$ROTATE.point",
                   "{0} 0 0 {1}".format(self.rotationSpeed, r))
    def recordRotationSpeedOnce(self):
        if (self.rotationSpeed is not None):
            return
        self.c.setConst("ROTATE", FILTER_ACTION_ROTATE)
        p = self.c.get("$ROTATE.point")[0]
        self.rotationSpeed = p.split(" ")[0]
    def setAcceptTile(self, key, value):
        self.lastAcceptedTile = value[0]
        self.tiles[self.lastFreeSlotID] = self.lastAcceptedTile
        freeLeaf = FILTER_LEAF_PREFIX + str(self.lastFreeSlotID)
        self.c.setConst("TILE", self.lastAcceptedTile)
        self.c.set("node.$SCENE.$TILE.parentAbs", freeLeaf)
    # alignFreeSlotWithSource.
    def setAlignFreeSlotWithSource(self, key, value):
        self.recordRotationSpeedOnce()
        self.findFreeSlot()
        self.prepareTargetRotation()
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.onAlignFinish)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
    # createTile.
    def setCreateTile(self, key, value):
        # Create tile.
        tileName = self.c.get("tileFactory.createTile")[0]
        # Attach to leaf.
        self.c.setConst("TILE", tileName)
        self.c.set("node.$SCENE.$TILE.parent",
                   FILTER_LEAF_PREFIX + str(FILTER_LEAF_FILTER_ID))
        self.c.set("node.$SCENE.$TILE.position", FILTER_TILE_INITIAL_POS)
        self.tiles[FILTER_LEAF_FILTER_ID] = tileName
        self.c.report("filter.createTile", "0")
    # dropLastAcceptedTile.
    def setDropLastAcceptedTile(self, key, value):
        print "droplast accepted tile", self.lastAcceptedTile
        self.c.setConst("DROP", FILTER_ACTION_DROP_ACCEPTED_TILE)
        self.c.listen("$DROP.$SCENE.$TILE.active",
                      "0",
                      self.onAcceptedTileDropped)
        self.c.set("$DROP.$SCENE.$TILE.active", "1")
    # dropLastCreatedTile.
    def setDropLastCreatedTile(self, key, value):
        tileName = None
        for slot, tile in self.tiles.items():
            if (tile is not None):
                tileName = tile
                break
        self.c.setConst("DROP", FILTER_ACTION_DROP_NEW_TILE)
        self.c.listen("$DROP.$SCENE.$TILE.active", "0", self.onTileDropped)
        self.c.set("$DROP.$SCENE.$TILE.active", "1")

class Filter(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Filter")
        self.impl = FilterImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("filter.acceptTile", self.impl.setAcceptTile)
        self.c.provide("filter.alignFreeSlotWithSource",
                       self.impl.setAlignFreeSlotWithSource)
        self.c.provide("filter.createTile",  self.impl.setCreateTile)
        self.c.provide("filter.dropLastAcceptedTile",
                       self.impl.setDropLastAcceptedTile)
        self.c.provide("filter.dropLastCreatedTile",
                       self.impl.setDropLastCreatedTile)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Filter(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

