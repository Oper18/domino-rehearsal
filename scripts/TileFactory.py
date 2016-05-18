
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
        self.pairs = []
        self.pairsFreeNb = 0
        # Generate all possible tile halves' combinations.
        for i in xrange(TILE_VALUE_MIN, TILE_VALUE_MAX + 1):
            for j in xrange(i, TILE_VALUE_MAX + 1):
                self.pairs.append({ "i" : i,
                                    "j" : j,
                                 "free" : True })
                self.pairsFreeNb = self.pairsFreeNb + 1
    def __del__(self):
        self.c = None
    def tileMaterial(self):
        # Select random free pair.
        random.seed()
        id = random.randint(0, self.pairsFreeNb - 1)
        i = 0
        pair = None
        for p in self.pairs:
            if (p["free"]):
                if (i == id):
                    pair = p
                    break
                i = i + 1
        # Use it.
        pair["free"] = False
        self.pairsFreeNb = self.pairsFreeNb - 1
        mat = "{0}{1}{2}".format(TILE_MATERIAL_PREFIX, pair["i"], pair["j"])
        return mat
    # createTile.
    def getCreateTile(self, key):
        self.lastTileID = self.lastTileID + 1
        tileName = "tile{0}".format(self.lastTileID)
        self.c.setConst("TILE", tileName)
        self.c.set("node.$SCENE.$TILE.parent",     "ROOT")
        self.c.set("node.$SCENE.$TILE.model",      TILE_MODEL)
        self.c.set("node.$SCENE.$TILE.material",   self.tileMaterial())
        self.c.set("node.$SCENE.$TILE.selectable", "1")
        return [tileName]
    # freeTile.
    def setFreeTile(self, key, value):
        self.c.setConst("TILE", value[0])
        mat = self.c.get("node.$SCENE.$TILE.material")[0]
        i = int(mat[-2])
        j = int(mat[-1])
        for p in self.pairs:
            if (not p["free"]):
                if ((p["i"] == i) and
                    (p["j"] == j)):
                    p["free"] = True
                    break

class TileFactory(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "TileFactory")
        self.impl = TileFactoryImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.provide("tileFactory.createTile", None, self.impl.getCreateTile)
        self.c.provide("tileFactory.freeTile",   self.impl.setFreeTile)
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

