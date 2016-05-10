
from pymjin2 import *

LCD_MATERIAL_NAME_PREFIX = "lcd_digit"

class LCDImpl(object):
    def __init__(self, c):
        self.c = c
        self.digits = []
    def __del__(self):
        self.c = None
    def locateDigitNodesOnce(self):
        # Only do it once.
        if (len(self.digits)):
            return
        # Children are digits.
        self.digits = self.c.get("node.$SCENE.$NODE.children")
    def setDigitValue(self, digitID, value):
        self.c.setConst("DIGIT", self.digits[digitID])
        material = LCD_MATERIAL_NAME_PREFIX + value
        self.c.set("node.$SCENE.$DIGIT.material", material)
    def setValue(self, key, value):
        self.locateDigitNodesOnce()
        strval = value[0]
        # Display nothing if:
        # * Value is longer than we can display.
        # * Value is none.
        if ((len(strval) > len(self.digits)) or
            not len(strval)):
            for i in xrange(0, len(self.digits)):
                self.setDigitValue(i, "")
            return
        # Divide string value into separate digits.
        # Use empty value for padded digits.
        start = len(self.digits) - len(strval)
        for i in xrange(0, len(self.digits)):
            # Digit.
            if (i >= start):
                self.setDigitValue(i, strval[i - start])
            # Padding.
            else:
                self.setDigitValue(i, "")

class LCD(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "LCD/" + nodeName)
        self.impl = LCDImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.provide("lcd.$SCENE.$NODE.value", self.impl.setValue)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return LCD(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

