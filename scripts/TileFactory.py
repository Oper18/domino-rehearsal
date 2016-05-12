
from pymjin2 import *
import random

TILE_MATERIAL_PREFIX = "tile"
TILE_MODEL           = "models/tile.osgt"
TILE_VALUE_MIN       = 0
TILE_VALUE_MAX       = 6

class TileFactoryImpl(object):
    def __init__(self, c):
        self.c = c
        self.lastTileID = 0
    def __del__(self):
        self.c = None
    def randomTileMaterial(self):
        random.seed()
        # TODO: generate left and right values correctly,
        # TODO: not all pairs exist.
        i = random.randint(TILE_VALUE_MIN, TILE_VALUE_MAX)
        mat = "{0}{1}{2}".format(TILE_MATERIAL_PREFIX, i, i)
        print "material", mat
        return mat
    def getCreateTile(self, key):
        print "getCreateTile", key
        self.lastTileID = self.lastTileID + 1
        tileName = "tile{0}".format(self.lastTileID)
        self.c.setConst("TILE", tileName)
        self.c.set("node.$SCENE.$TILE.parent",   "ROOT")
        self.c.set("node.$SCENE.$TILE.model",    TILE_MODEL)
        self.c.set("node.$SCENE.$TILE.material", self.randomTileMaterial())
        return [tileName]

class TileFactory(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "TileFactory")
        self.impl = TileFactoryImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.provide("tileFactory.createTile", None, self.impl.getCreateTile)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return TileFactory(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

