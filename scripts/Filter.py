
from pymjin2 import *

FILTER_ACTION_DROP_TILE      = "move.default.lowerTile"
FILTER_LEAF_FILTER_ID        = 0
FILTER_LEAF_PREFIX           = "filterLeaf"
FILTER_TILE_INITIAL_POS      = "0 0 11"

class FilterImpl(object):
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
        self.c.set("node.$SCENE.$TILE.parent",   FILTER_LEAF_PREFIX + str(id))
        self.c.set("node.$SCENE.$TILE.position", FILTER_TILE_INITIAL_POS)
        self.tiles.append(tileName)
        self.c.report("filter.createTile", "0")
    # dropLastCreatedTile.
    def onTileDropped(self, key, value):
        self.c.unlisten("$DROP.$SCENE.$TILE.active")
        self.c.report("filter.dropLastCreatedTile", "0")
    def setDropLastCreatedTile(self, key, value):
        tileName = self.tiles[len(self.tiles) - 1]
        self.c.setConst("DROP", FILTER_ACTION_DROP_TILE)
        self.c.listen("$DROP.$SCENE.$TILE.active", "0", self.onTileDropped)
        self.c.set("$DROP.$SCENE.$TILE.active", "1")

class Filter(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Filter")
        self.impl = FilterImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("filter.createTile",  self.impl.setCreateTile)
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

