
from pymjin2 import *

SOURCE_ACTION_DROP_TILE      = "move.default.lowerTile"
SOURCE_LEAF_PREFIX           = "sourceLeaf"
SOURCE_TILE_INITIAL_POS      = "0 0 9"

class SourceImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = []
    def __del__(self):
        self.c = None
    # createTile.
    def setCreateTile(self, key, value):
        id = len(self.tiles)
        # Create tile.
        tileName = self.c.get("tileFactory.createTile")[0]
        # Attach to leaf.
        self.c.setConst("TILE", tileName)
        self.c.set("node.$SCENE.$TILE.parent",   SOURCE_LEAF_PREFIX + str(id))
        self.c.set("node.$SCENE.$TILE.position", SOURCE_TILE_INITIAL_POS)
        self.tiles.append(tileName)
        self.c.report("source.createTile", "0")
    # dropLastCreatedTile.
    def onTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("source.dropLastCreatedTile", "0")
    def setDropLastCreatedTile(self, key, value):
        tileName = self.tiles[len(self.tiles) - 1]
        self.c.setConst("DROP", SOURCE_ACTION_DROP_TILE)
        self.c.listen("$DROP.$SCENE.$TILE.active", "0", self.onTileDropped)
        self.c.set("$DROP.$SCENE.$TILE.active", "1")
    # markTilesSelectable.
    def setMarkTilesSelectable(self, key, value):
        for tileName in self.tiles:
            self.c.setConst("TILE", tileName)
            self.c.set("node.$SCENE.$TILE.selectable", "1")
        self.c.report("source.markTilesSelectable", "0")

class Source(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Source")
        self.impl = SourceImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("source.createTile",  self.impl.setCreateTile)
        self.c.provide("source.dropLastCreatedTile",
                       self.impl.setDropLastCreatedTile)
        self.c.provide("source.markTilesSelectable",
                       self.impl.setMarkTilesSelectable)
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

