
from pymjin2 import *

FILTER_ACTION_DROP_ACCEPTED_TILE  = "move.default.dropFilterTile"
FILTER_ACTION_DROP_NEW_TILE       = "move.default.lowerTile"
FILTER_ACTION_DROP_UNMATCHED_TILE = "move.default.dropUnmatchedTile"
FILTER_ACTION_ROTATE              = "rotate.default.rotateFilter"
FILTER_LEAF_FILTER_ID             = 0
FILTER_LEAF_PREFIX                = "filterLeaf"
FILTER_SLOTS_NB                   = 3
FILTER_SEQUENCE_ALGORITHM_FAILURE = "esequence.default.algorithmFailure"
FILTER_SEQUENCE_ALGORITHM_SUCCESS = "esequence.default.algorithmSuccess"
FILTER_TILE_INITIAL_POS           = "0 0 11"

class FilterImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = {}
        for i in xrange(0, FILTER_SLOTS_NB):
            self.tiles[i] = None
        self.lastAcceptedTile = None
        self.lastFreeSlotID = None
        self.lastUsedSlotID = None
        self.rotationSpeed = None
    def __del__(self):
        self.c = None
    def findFreeSlot(self):
        self.lastFreeSlotID = None
        for slot, tile in self.tiles.items():
            if (tile is None):
                self.lastFreeSlotID = slot
                break
    def findUsedSlot(self):
        self.lastUsedSlotID = None
        for slot, tile in self.tiles.items():
            # Ignore filter slot.
            if (slot == FILTER_LEAF_FILTER_ID):
                continue
            if (tile is not None):
                self.lastUsedSlotID = slot
                break
    # lastUsedTile.
    def getLastUsedTile(self, key):
        return [self.tiles[self.lastUsedSlotID]]
    # dropLastAcceptedTile.
    def onAcceptedTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("filter.dropLastAcceptedTile", "0")
    # ifNoFreeSlotsPerformAlgorithm.
    def onAlgorithmFinish(self, key, value):
        self.c.unlisten("$SEQ.active")
        self.c.report("filter.ifNoFreeSlotsPerformAlgorithm", "0")
    # alignFreeSlotWithSource.
    def onAlignFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("filter.alignFreeSlotWithSource", "0")
    # alignUsedSlotWithDestination.
    def onAlignDstFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("filter.alignUsedSlotWithDestination", "0")
    # dropLastCreatedTile.
    def onTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("filter.dropLastCreatedTile", "0")
    # returnToInitialRotation.
    def onReturnToInitialRotationFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("filter.returnToInitialRotation", "0")
    # dropUnmatchedTile.
    def onUnmatchedTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("filter.dropUnmatchedTile", "0")
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
    def prepareRotationToDst(self):
        # Set new rotation.
        r = 90 - 120 * self.lastUsedSlotID + 180
        self.c.set("$ROTATE.point",
                   "{0} 0 0 {1}".format(self.rotationSpeed, r))
    # acceptTile.
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
    # alignUsedSlotWithDestination.
    def setAlignUsedSlotWithDestination(self, key, value):
        self.findUsedSlot()
        self.prepareRotationToDst()
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.onAlignDstFinish)
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
    # destroyUnmatchedTile.
    def setDestroyUnmatchedTile(self, key, value):
        self.c.set("node.$SCENE.$TILE.parent", "")
        self.c.report("filter.destroyUnmatchedTile", "0")
    # dropLastAcceptedTile.
    def setDropLastAcceptedTile(self, key, value):
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
    # dropUnmatchedTile.
    def setDropUnmatchedTile(self, key, value):
        tileName = None
        for slot, tile in self.tiles.items():
            if (slot == FILTER_LEAF_FILTER_ID):
                continue
            if (tile is not None):
                tileName = tile
                self.tiles[slot] = None
                break
        self.c.setConst("DROP", FILTER_ACTION_DROP_UNMATCHED_TILE)
        self.c.setConst("TILE", tileName)
        self.c.listen("$DROP.$SCENE.$TILE.active", "0", self.onUnmatchedTileDropped)
        self.c.set("$DROP.$SCENE.$TILE.active", "1")
    # ifNoFreeSlotsPerformAlgorithm.
    def setIfNoFreeSlotsPerformAlgorithm(self, key, value):
        # Make sure there are no free slots.
        full = True
        for slot, tile in self.tiles.items():
            if (tile is None):
                full = False
                break
        # Do nothing if any slot is empty.
        if (not full):
            self.c.report("filter.ifNoFreeSlotsPerformAlgorithm", "0")
            return
        # Perform algorithm.
        # THIS IS A SIMPLIFIED MATCHING ALGORITHM: simply check
        # if all tiles are equal.
        # TODO: rewrite to use full version of the algorithm.
        # Use tile material to compare equality.
        # It's ugly, but fine for now.
        lastTileMat = None
        allTilesAreEqual = True
        for slot, tile in self.tiles.items():
            self.c.setConst("TILE", tile)
            mat = self.c.get("node.$SCENE.$TILE.material")[0]
            if (lastTileMat is None):
                lastTileMat = mat
            elif (lastTileMat != mat):
                allTilesAreEqual = False
                break
        # Run success sequence.
        if (allTilesAreEqual):
            self.c.setConst("SEQ", FILTER_SEQUENCE_ALGORITHM_SUCCESS)
            self.c.listen("$SEQ.active", "0", self.onAlgorithmFinish)
            self.c.set("$SEQ.active", "1")
        # Run failure sequence.
        else:
            self.c.setConst("SEQ", FILTER_SEQUENCE_ALGORITHM_FAILURE)
            self.c.listen("$SEQ.active", "0", self.onAlgorithmFinish)
            self.c.set("$SEQ.active", "1")
    # removeUsedTile.
    def setRemoveUsedTile(self, key, value):
        for slot, tile in self.tiles.items():
            if (slot == self.lastUsedSlotID):
                self.tiles[slot] = None
                self.lastUsedSlotID = None
                break
    # returnToInitialRotation.
    def setReturnToInitialRotation(self, key, value):
        # Set initial rotation.
        self.c.set("$ROTATE.point", "{0} 0 0 0".format(self.rotationSpeed))
        self.c.listen("$ROTATE.$SCENE.$NODE.active",
                      "0",
                      self.onReturnToInitialRotationFinish)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")

class Filter(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Filter")
        self.impl = FilterImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("filter.acceptTile", self.impl.setAcceptTile)
        self.c.provide("filter.alignFreeSlotWithSource",
                       self.impl.setAlignFreeSlotWithSource)
        self.c.provide("filter.alignUsedSlotWithDestination",
                       self.impl.setAlignUsedSlotWithDestination)
        self.c.provide("filter.createTile",  self.impl.setCreateTile)
        self.c.provide("filter.destroyUnmatchedTile",
                       self.impl.setDestroyUnmatchedTile)
        self.c.provide("filter.dropLastAcceptedTile",
                       self.impl.setDropLastAcceptedTile)
        self.c.provide("filter.dropLastCreatedTile",
                       self.impl.setDropLastCreatedTile)
        self.c.provide("filter.dropUnmatchedTile",
                       self.impl.setDropUnmatchedTile)
        self.c.provide("filter.ifNoFreeSlotsPerformAlgorithm",
                       self.impl.setIfNoFreeSlotsPerformAlgorithm)
        self.c.provide("filter.lastUsedTile", None, self.impl.getLastUsedTile)
        self.c.provide("filter.removeUsedTile", self.impl.setRemoveUsedTile)
        self.c.provide("filter.returnToInitialRotation",
                       self.impl.setReturnToInitialRotation)
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

