
from pymjin2 import *

MAIN_BALL_NAME   = "ball"
MAIN_SOUND_START = "soundBuffer.default.start"

class MainImpl(object):
    def __init__(self, c):
        self.c = c
    def __del__(self):
        self.c = None
    def onBallStopped(self, key, value):
        print "Ball stopped"
    def onSpace(self, key, value):
        print "Space pressed. Replay sound. Rotate the ball"
        self.c.set("$SNDSTART.state", "play")
        self.c.set("$BALL.$SCENE.$BALL.moving", "1")

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        self.c.setConst("SCENE",    sceneName)
        self.c.setConst("BALL",     MAIN_BALL_NAME)
        self.c.setConst("SNDSTART", MAIN_SOUND_START)
        self.c.listen("input.SPACE.key", "1", self.impl.onSpace)
        self.c.listen("$BALL.$SCENE.$BALL.moving", "0", self.impl.onBallStopped)
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

