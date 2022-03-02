import random
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pynput.mouse
from pynput import keyboard
from pynput.mouse import Listener
import UtilityModules
import time
import ctypes
import math

Bitmapping = UtilityModules.Bitmaps()

class Afk:

    def __init__(self, CollectionPath):
        self.LastAction = time.time()
        self.KickInDelay = 0.5
        self.Collection = CollectionPath
        self.DelayBetweenRp = 5
        self.TimeInDelay = 0
        self.BetweenRp = Bitmapping.CreateEmptyBitmap(128,40)
        self.Transition = 'Animations/LaggedSlideFade'
        self.StartAnimation = 'Animations/RoundEyesInvert'
        self.RepeatAnimation = 'Animations/RepeatBreath'
        self.EndingTransition = 'Animations/ReverseSlideFade'
        self.Startup = UtilityModules.Sprite(self.Transition,self.StartAnimation)
        self.Rp = UtilityModules.Sprite(self.RepeatAnimation, RepeatOnFinished=True)
        self.End = UtilityModules.Sprite(self.EndingTransition)

    def RegisterAction(self,a="a",b="b",c="c",d="d"):
        self.LastAction = time.time()

    def Start(self):
        keyboardListener = keyboard.Listener(on_press=self.RegisterAction)
        keyboardListener.start()
        self.mouseListener = Listener(on_move= self.RegisterAction, on_click= self.RegisterAction, on_scroll= self.RegisterAction)
        self.mouseListener.start()
        a = 0
        while True:
            if a >= self.Collection.FPS:
                if time.time() - self.LastAction > (self.KickInDelay * 60):
                    self.Collection.RequestOverride(Afk)
            else: a += 1
            time.sleep(1/self.Collection.FPS)

    def Return_base(self):
        if time.time() - self.LastAction > (self.KickInDelay * 60) or self.Startup.FrameOn != 0 and self.Startup.finished == False:
            if self.Startup.finished == False:
                B = self.Startup.next()
            elif self.TimeInDelay == self.DelayBetweenRp*self.Collection.FPS:
                B = self.Rp.next()
                if self.Rp.finished == True:
                    self.TimeInDelay = 0
            else:
                self.TimeInDelay += 1
                B = self.BetweenRp
            return B
        else:
            if self.Rp.finished != True and self.Rp.FrameOn != -1:
                return self.Rp.next()
            elif self.End.finished != True:
                return self.End.next()
            else:
                self.Collection.EndOverride()
                self.Startup.reset()
                self.Rp.reset()
                self.End.reset()
                self.TimeInDelay = 0

class Keystroke_logging:

    class Keydata:
        def __init__(self,Letter,Offset,sprite,DivideFrame = 5):
            self.Letter = Letter
            self.Offset = Offset
            self.Sprite = sprite
            self.DivideFrame = DivideFrame
            self.Mode = None

    class MouseButton:
        def __init__(self,sprite):
            self.Sprite = sprite
            self.Mode = None

    def __init__(self, CollectionPath):
        self.KeyboardSet = "ShadowedKeyboard"
        self.Collection = CollectionPath
        self.Base = Bitmapping.ImportBitmapFromPNG(f"Animations/{self.KeyboardSet}.png")
        self.Background = Bitmapping.CreateEmptyBitmap(128,40)
        self.MouseOverlay = Bitmapping.CreateEmptyBitmap(128,40,2)
        self.WPM = 0
        a = {"Q": (10,1), "W": (21,1), "E": (32,1), "R": (43,1), "T": (54,1), "Y": (65,1), "U": (76,1),
                              "I": (87,1), "O": (98,1), "P": (109,1), "A": (15,11), "S": (26,11),"D": (37,11),
                              "F": (48,11), "G": (59,11), "H": (70,11), "J": (81,11), "K": (92,11), "L": (103,11),
                              "Z": (20,21), "X": (31,21), "C": (42,21), "V": (53,21), "B": (64,21), "N": (75,21),
                              "M": (86,21), "Key.space": (27,31)}
        self.KeyDictionary = {i:(self.Keydata(i, a[i], UtilityModules.Sprite(f"Animations/{self.KeyboardSet}/Button")) if i != "Key.space" else self.Keydata(i, a[i], UtilityModules.Sprite(f"Animations/{self.KeyboardSet}/Spacebar"))) for i in a}
        self.CtrlDictionary = {"\x11" : "Q", "\x17": "W", "\x05" : "E", "\x12" : "R", "\x14": "T", "\x19" : "Y",
                               "\x15" : "U", "\t" : "I", "\x0f" : "O", "\x10" : "P", "\x01" : "A", "\x13" : "S",
                               "\x04" : "D", "\x06" : "F", "\x07" : "G", "\x08" : "H", "\n" : "J", "\x0b" : "K",
                               "\x0c" : "L", "\x1a" : "Z", "\x18" : "X", "\x03" : "C", "\x16": "V", "\x02" : "B",
                               "\x0e" : "N", "\r" : "M"}
        self.KeyDictionary["Button.left"] = self.Keydata("Button.left",(0,0),UtilityModules.Sprite("Animations/LeftClick"),3)
        self.KeyDictionary["Button.right"] = self.Keydata("Button.right",(122,0),UtilityModules.Sprite("Animations/RightClick"),3)
        self.mouse = pynput.mouse.Controller()
        self.screensize = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self.maxGyro = (2,1)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.PastVolumeLevel = self.volume.GetMasterVolumeLevelScalar() * 100
        self.VolumeTransition = UtilityModules.Sprite("Animations/VolumeTransition")
        self.VolumeBuddy = UtilityModules.Sprite("Animations/VolumeBuddy", RepeatOnFinished=True, RepeatIndex=77)
        self.VolumeBar = UtilityModules.Sprite("Animations/VolumeBar")
        self.VolumeTime = 0

    def Return_base(self):
        if self.Collection.CurrentFrame == self.Collection.FPS:
            #print(self.WPM*60)
            self.WPM = 0
        #render keystrokes and mouse clicks
        for i in self.KeyDictionary.values():
            a = None
            if i.Mode == "release":
                if i.Sprite.FrameOn == len(i.Sprite.SpriteSet)-1:
                    i.Mode = None
                elif i.Sprite.FrameOn >= i.DivideFrame:
                    a = i.Sprite.next()
                elif i.Sprite.FrameOn < i.DivideFrame:
                    a = i.Sprite.seek(i.DivideFrame+1)
            elif i.Mode == "press":
                if i.Sprite.FrameOn > i.DivideFrame:
                    a = i.Sprite.seek(0)
                elif i.Sprite.FrameOn < i.DivideFrame:
                    a = i.Sprite.next()
            if a != None:
                self.Base = Bitmapping.AlterBitmap(self.Base, a, i.Offset)
        #start volume display if volume level was altered
        if (p := self.volume.GetMasterVolumeLevelScalar() * 100) != self.PastVolumeLevel or self.VolumeTime != 5*self.Collection.FPS and self.VolumeTime != 0:
            self.PastVolumeLevel = p
            self.VolumeTime += 1
            c = self.VolumeBuddy.next()
            if self.VolumeBuddy.SpriteNumber > (s := (math.floor(self.PastVolumeLevel/33)+1)*14-1) and self.VolumeBuddy.SpriteNumber % 14 == 0:
                c = self.VolumeBuddy.seekSprite(s-13)
            elif self.PastVolumeLevel == 100:
                self.VolumeBuddy.seekSprite(41)
            if not self.VolumeTransition.SpriteNumber >= 14:
                self.VolumeTime = 1
                C = Bitmapping.AlterBitmap(Bitmapping.Copy(c), self.VolumeTransition.next(), Invert=True,FullAlter=True)
                return Bitmapping.AlterBitmap(Bitmapping.Copy(self.Base), C)
            else:
                C = Bitmapping.AlterBitmap(Bitmapping.Copy(c), self.VolumeTransition.seek(self.VolumeTransition.FrameOn), Invert=True, FullAlter=True)
                if (l:=round(self.PastVolumeLevel/10)) > round((self.VolumeBar.FrameOn-1)/3):
                    self.VolumeTime = 1
                    b = self.VolumeBar.next()
                elif l < round((self.VolumeBar.FrameOn+1)/3):
                    self.VolumeTime = 1
                    b = self.VolumeBar.next(reverse=True)
                else:
                    b = self.VolumeBar.seek(self.VolumeBar.FrameOn)
                return Bitmapping.AlterBitmap(C, b, (44, 15))
        elif not self.VolumeTransition.finished and self.VolumeTransition.FrameOn > 0:
            c = self.VolumeBuddy.next()
            if self.VolumeBuddy.SpriteNumber > (s := (math.floor(self.PastVolumeLevel / 33) + 1) * 14 - 1) and self.VolumeBuddy.SpriteNumber % 14 == 0:
                c = self.VolumeBuddy.seekSprite(s - 13)
            if self.VolumeBar.FrameOn != 0:
                C = Bitmapping.AlterBitmap(Bitmapping.Copy(c), self.VolumeTransition.seek(self.VolumeTransition.FrameOn), Invert=True, FullAlter=True)
                return Bitmapping.AlterBitmap(C, self.VolumeBar.next(reverse=True), (44,15))
            if self.VolumeBar.FrameOn == 0:
                #print(self.VolumeTransition.SpriteNumber)
                return Bitmapping.AlterBitmap(Bitmapping.Copy(self.Base),Bitmapping.AlterBitmap(Bitmapping.Copy(c), self.VolumeTransition.next(), Invert=True, FullAlter=True))
        elif self.VolumeTime != 0:
            self.VolumeTime = 0
            self.VolumeTransition.reset()
            self.VolumeBar.reset()
        #return Bitmapping.AlterBitmap(Bitmapping.Copy(self.Background),self.Base,(round(self.mouse.position[0]/((s := self.screensize[0]/self.maxGyro[0]))),round(self.mouse.position[1]/((s := self.screensize[0]/self.maxGyro[1])))))
        return self.Base

    def Start(self):
        keylistener = keyboard.Listener(on_press=self.Press, on_release=self.Release)
        keylistener.start()
        mouselistener = Listener(on_click=self.Mouseclick)
        mouselistener.start()

    def Mouseclick(self,*args):
        try:
            if args[3]:
                self.KeyDictionary[str(args[2])].Mode = "press"
            else:
                self.KeyDictionary[str(args[2])].Mode = "release"
        except: pass

    def Press(self, key):
        self.WPM += 1/7
        try:
            try: k = key.char.capitalize() if key.char.isalpha() == True else x
            except: k = self.CtrlDictionary[key.char]
        except:
            if key == keyboard.Key.space: k = "Key.space"
            else: return 0
        self.KeyDictionary[k].Mode = "press"

    def Release(self, key):
        try:
            try: k = key.char.capitalize() if key.char.isalpha() == True else x
            except: k = self.CtrlDictionary[key.char]
        except:
            if key == keyboard.Key.space: k = "Key.space"
            else: return 0
        self.KeyDictionary[k].Mode = "release"

class TestModule:

    def __init__(self, CollectionPath):
        self.Base = Bitmapping.CreateEmptyBitmap(128,40,1)
        self.Base = Bitmapping.AlterBitmap(self.Base, Bitmapping.CreateEmptyBitmap(10,10,1), (random.randint(0,100),random.randint(0,100)), True)
        self.Collection = CollectionPath

    def Start(self):
        time.sleep(3)
        self.Collection.RequestOverride(TestModule)


    def Return_base(self):
        return self.Base
