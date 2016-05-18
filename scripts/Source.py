
from pymjin2 import *

SOURCE_ACTION_DROP_TILE      = "move.default.lowerTile"
SOURCE_ACTION_ROTATE         = "rotate.default.rotateSource"
SOURCE_FILTER_NAME           = "filter"
SOURCE_LEAF_PREFIX           = "sourceLeaf"
SOURCE_SEQUENCE_SELECTION    = "esequence.default.sourceTileSelection"
SOURCE_SLOTS_NB              = 6
SOURCE_TILE_INITIAL_POS      = "0 0 9"

class SourceImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = {}
        for i in xrange(0, SOURCE_SLOTS_NB):
            self.tiles[i] = None
        self.rotationSpeed = None
        self.lastSelectedTileName = None
    def __del__(self):
        self.c = None
    def getLastSelectedTile(self, key):
        return [self.lastSelectedTileName]
    # result.
    def getResult(self, key):
        res = 0
        for slot, tile in self.tiles.items():
            self.c.setConst("TILE", tile)
            mat = self.c.get("node.$SCENE.$TILE.material")[0]
            i = int(mat[-2])
            j = int(mat[-1])
            res = res + i + j
        return [str(res)]
    # alignSelectedTileWithFilter.
    def onAlignFinish(self, key, value):
        self.c.unlisten("$ROTATE.$SCENE.$NODE.active")
        self.c.report("source.alignSelectedTileWithFilter", "0")
    # dropLastCreatedTile.
    def onTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("source.dropLastCreatedTile", "0")
    def onTileSelection(self, key, value):
        self.lastSelectedTileName = key[2]
        self.c.setConst("SEQ", SOURCE_SEQUENCE_SELECTION)
        self.c.set("$SEQ.active", "1")
    def prepareTargetRotation(self):
        # Convert tile name to slot ID.
        slotID = None
        for slot, tile in self.tiles.items():
            if (tile == self.lastSelectedTileName):
                slotID = slot
                break
        # Set new rotation.
        r = -60 * slotID - 90
        self.c.set("$ROTATE.point",
                   "{0} 0 0 {1}".format(self.rotationSpeed, r))
    def recordRotationSpeedOnce(self):
        if (self.rotationSpeed is not None):
            return
        self.c.setConst("ROTATE", SOURCE_ACTION_ROTATE)
        p = self.c.get("$ROTATE.point")[0]
        self.rotationSpeed = p.split(" ")[0]
    # alignSelectedTileWithFilter.
    def setAlignSelectedTileWithFilter(self, key, value):
        self.recordRotationSpeedOnce()
        self.prepareTargetRotation()
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.onAlignFinish)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
    # allowTileSelection.
    def setAllowTileSelection(self, key, value):
        for slot, tile in self.tiles.items():
            if (tile is not None):
                self.c.setConst("TILE", tile)
                self.c.listen("node.$SCENE.$TILE.selected",
                              "1",
                              self.onTileSelection)
        self.c.report("source.allowTileSelection", "0")
    # createTile.
    def setCreateTile(self, key, value):
        slotID = None
        # Find free slot.
        for slot, tile in self.tiles.items():
            if (tile is None):
                slotID = slot
                break
        # Create tile.
        tileName = self.c.get("tileFactory.createTile")[0]
        # Attach to leaf.
        self.c.setConst("TILE", tileName)
        self.c.set("node.$SCENE.$TILE.parent",   SOURCE_LEAF_PREFIX + str(slotID))
        self.c.set("node.$SCENE.$TILE.position", SOURCE_TILE_INITIAL_POS)
        self.tiles[slotID] = tileName
        self.c.report("source.createTile", "0")
    # disallowTileSelection.
    def setDisallowTileSelection(self, key, value):
        for slot, tile in self.tiles.items():
            if (tile is not None):
                self.c.setConst("TILE", tile)
                self.c.unlisten("node.$SCENE.$TILE.selected")
        self.c.report("source.disallowTileSelection", "0")
    # dropLastCreatedTile.
    def setDropLastCreatedTile(self, key, value):
        # TILE const has been set during creation.
        self.c.setConst("DROP", SOURCE_ACTION_DROP_TILE)
        self.c.listen("$DROP.$SCENE.$TILE.active", "0", self.onTileDropped)
        self.c.set("$DROP.$SCENE.$TILE.active", "1")
    # removeSelectedTile.
    def setRemoveSelectedTile(self, key, value):
        for slot, tile in self.tiles.items():
            if (tile == self.lastSelectedTileName):
                self.tiles[slot] = None
                self.lastSelectedTileName = None
                break

class Source(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Source")
        self.impl = SourceImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("source.alignSelectedTileWithFilter",
                       self.impl.setAlignSelectedTileWithFilter)
        self.c.provide("source.allowTileSelection",
                       self.impl.setAllowTileSelection)
        self.c.provide("source.createTile",  self.impl.setCreateTile)
        self.c.provide("source.disallowTileSelection",
                       self.impl.setDisallowTileSelection)
        self.c.provide("source.dropLastCreatedTile",
                       self.impl.setDropLastCreatedTile)
        self.c.provide("source.lastSelectedTile",
                       None,
                       self.impl.getLastSelectedTile)
        self.c.provide("source.removeSelectedTile",
                       self.impl.setRemoveSelectedTile)
        self.c.provide("source.result", None, self.impl.getResult)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Source(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

