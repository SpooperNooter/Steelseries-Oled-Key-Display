import time
import threading
import requests
import os
import json
from PIL import Image
import math

#Module for collecting finished Bitmaps
class PacketCollection:

    def __init__(self):
        self.OverrideQueue = []
        self.Default = "Keystroke_logging.1"
        self.Path = self.Default
        self.ClassInstance = {}
        self.FPS = 30
        self.StartTime = 0
        self.CurrentFrame = 0

    def RequestOverride(self, Path):
        P = "%s.1" % Path.__name__
        m = "Function already requested override"
        if self.Path == P:
            return m
        try:
            self.OverrideQueue.index(P)
            return m
        except:
            if self.Path != self.Default:
                self.OverrideQueue.append(P)
                print(P)
                print("%s requested override, override %s in place, adding request to queue." % P[0:(len(P)-2)], self.Path[0:(len(self.Path)-2)])
            else:
                self.Path = P
                print("%s requested override, no current override in place" % P[0:(len(P)-2)])

    def EndOverride(self):
        print("%s override ending, path set to default" % self.Path[0:(len(self.Path) - 2)])
        self.Path = self.Default

    def StartCollection(self):
        self.StartTime = time.time_ns()
        while True:
            start = time.time()
            r = self.ClassInstance[self.Path].Return_base()
            if r == None:
                r = self.ClassInstance[self.Path].Return_base()
                for i in r:
                    try:
                        i.index(2)
                        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                    except: pass
            if self.Path != self.Default:
                for e in r:
                    try:
                        e.index(2)
                        r = Bitmapping.AlterBitmap(Bitmapping.Copy(self.ClassInstance[self.Default].Return_base()), r, [0,0])
                        break
                    except: pass
            R = Bitmapping.CompressBitmap(r)
            metadata = {"game": "REACTIVE_KEYBOARD_WIDGET",
                        "event": "KEY_UPDATE",
                        "data": {
                            "value": Posting.value_lottery(),
                            "frame": {
                                "image-data": R
                            }}}
            Posting.Post(metadata, "/game_event")
            if self.CurrentFrame < self.FPS: self.CurrentFrame += 1
            else: self.CurrentFrame = 0
            if (m := time.time() - start) > 1/self.FPS: print(m)
            else: time.sleep((1/self.FPS)-m)

def InstansiateCollection():
    global ModuleManaging
    ModuleManaging = PacketCollection()
    return ModuleManaging

ShadingLevelPath = 'Animations/ShadingLevels.png'
L = list((Image.open('Animations/ShadingLevels.png').convert('RGBA').getdata()))
ShadingLevels = [[[k if (k := round(sum(L[((g[1] + i) * 1920) + g[0] + I][0:2]) / 765)) == 1 else 2 for I in range(128)] for i in range(40)] for g in [(75, 19), (207, 19), (339, 19), (469, 19), (600, 19), (731, 19), (862, 19), (993, 19),(1124, 19), (1255, 19), (1386, 19)]]


#Module for creating raw bitmaps
class Bitmaps:

    #CreateEmptyBitmap and RoundCorners are for primitive bitmap creation and manipulation, probably should only be used for testing
    #Creates a bitmap with height and value according to input, with all positions as IntValue
    def CreateEmptyBitmap(self, Width, Height, IntValue = 0):
        EmptyBitmap = []
        EmptyLine = []
        for e in range(Height):
            for e in range(Width):
                EmptyLine.append(IntValue)
            EmptyBitmap.append(EmptyLine)
            EmptyLine = []
        return EmptyBitmap

    #Takes off the corners of the bitmap
    def RoundCorners(self,Bitmap):
        Bitmap[0][0] = 2
        Bitmap[0][(len(Bitmap[0])-1)] = 2
        Bitmap[(len(Bitmap)-1)][0] = 2
        Bitmap[(len(Bitmap)-1)][(len(Bitmap[0])-1)] = 2
        return Bitmap

    #Import an animation sheet png, convert it into a RGBA standard, then slice it documented size
    def ImportBitmapFromPNG(self,FilePath):
        try: a = list((Image.open(FilePath)).convert('RGBA').getdata())
        except Exception as Except: raise ImportError("Error with passed input variable, %s" % Except)
        BitmapSize = Image.open(FilePath).size
        Bitmap = [[round(sum(B[0:2])/765) if ShadingLevels[round((B := a[(i*BitmapSize[0])+I])[3]/25.5)][i][I] != 2 else 2 for I in range(BitmapSize[0])] for i in range(BitmapSize[1])]
        return Bitmap

    #Creates exact copy of bitmap, I created because of how python handles variables
    def Copy(self,CopyTo):
        return self.AlterBitmap(self.CreateEmptyBitmap(len(CopyTo[0]),len(CopyTo),2),CopyTo)

    #Alters the bitmap given with an alteration bitmap, at the offset given
    def AlterBitmap(self, BitmapPacket, AlterationPacket, Offset=[0,0], Invert=False, FullAlter=False):
        VerticalPosition = 0
        HorizontalPosition = 0
        for e in AlterationPacket:
            for E in AlterationPacket[VerticalPosition]:
                if (P := AlterationPacket[VerticalPosition][HorizontalPosition]) == 0 or P == 1 or FullAlter:
                    try:
                        BitmapPacket[VerticalPosition + Offset[1]][HorizontalPosition + Offset[0]] = ((1 if BitmapPacket[VerticalPosition + Offset[1]][HorizontalPosition + Offset[0]] == 0 else p) if Invert and p != 2 else p) if (p := AlterationPacket[VerticalPosition][HorizontalPosition]) == 1 or FullAlter else 0
                    except: break
                HorizontalPosition += 1
            HorizontalPosition = 0
            VerticalPosition += 1
        return BitmapPacket

    #Creates one list from a 2d list, then convert it to greatest bit first byte order
    def CompressBitmap(self,Bitmap):
        CompletedBitmap = []
        CompressedByte = 0
        BitDigit = 8
        for a in Bitmap:
            for e in a:
                BitDigit -= 1
                CompressedByte += (e*pow(2,BitDigit))
                if BitDigit == 0:
                    CompletedBitmap.append(CompressedByte)
                    CompressedByte  = 0
                    BitDigit = 8
        return CompletedBitmap

# Creates a class to manage sprite sheets
class Sprite:

    def __init__(self, *SpriteSheet, RepeatOnFinished = False, RepeatIndex = -1):
        self.Data = {i:json.load(open(f"Animations/{i}/info.json")) for i in SpriteSheet}
        for i in self.Data:
            if self.Data[i]["meta"]["app"] != "http://www.aseprite.org/": raise ImportError(f"Sprite sheet {self.Data.index(i)} is not in a valid format")
        self.SpriteSet = [I for e in SpriteSheet for I in self.SliceSheet(e)]
        self.FrameInfo = self.SpriteSet[0]["data"]
        self.FrameOn = -1
        self.SpriteNumber = 0
        self.finished = False
        self.Repeat = RepeatOnFinished
        self.RepeatIndex = RepeatIndex
        a = 0
        for i in self.SpriteSet:
            a += i["duration"]
        self.Length = math.floor(a/(1000/ModuleManaging.FPS))

    def SliceSheet(self, SpriteName):
        path = f"Animations/{SpriteName}/sheet.png"
        raw = list((Image.open(path)).convert('RGBA').getdata())
        sheetSize = Image.open(path).size
        Slices = [{"name": g, "duration": self.Data[SpriteName]["frames"][g]["duration"],"data": self.Data[SpriteName]["frames"][g],"bitmap" : [[round(sum(m[0:2]) / 765) if ShadingLevels[round((m := raw[((self.Data[SpriteName]["frames"][g]["frame"]["y"] + i) * sheetSize[0]) + I + self.Data[SpriteName]["frames"][g]["frame"]["x"]])[3] / 25.5)][i][I] != 2 else 2 for I in range(self.Data[SpriteName]["frames"][g]["frame"]["w"])] for i in range(self.Data[SpriteName]["frames"][g]["frame"]["h"])]} for g in self.Data[SpriteName]["frames"]]
        return Slices

    def next(self,if_finished = False,reverse = False):
        self.FrameOn += (1 if not reverse else -1)
        if reverse and self.FrameOn < 0:
            if not self.Repeat:
                raise IndexError("Cannot get previous frame")
            else:
                self.FrameOn = self.Length*1
        b = self.FrameOn*1
        for i in self.SpriteSet:
            b -= (i["duration"]/(1000/ModuleManaging.FPS))
            if b <= 0:
                self.SpriteNumber = self.SpriteSet.index(i)
                self.FrameInfo = i["data"]
                if i == self.SpriteSet[len(self.SpriteSet)-1]:
                    self.finished = True
                    if self.Repeat:
                        self.FrameOn = self.RepeatIndex
                else: self.finished = False
                return i["bitmap"]
        self.finished = True
        if self.Repeat:
            self.FrameOn = self.RepeatIndex
        else:
            self.FrameInfo = None
            return if_finished

    def seek(self,index):
        self.FrameOn = index
        b = self.FrameOn * 1
        for i in self.SpriteSet:
            b -= (i["duration"] / (1000 / ModuleManaging.FPS))
            if b <= 0:
                self.SpriteNumber = self.SpriteSet.index(i)
                self.FrameInfo = i["data"]
                self.finished = i == self.SpriteSet[len(self.SpriteSet) - 1]
                return i["bitmap"]
        raise IndexError(f"index {index} does not exist in SpriteSet")

    def seekSprite(self,index):
        if self.SpriteNumber == index:
            return self.seek(self.FrameOn)
        self.reset()
        while self.SpriteNumber != index:
            b = self.next()
        return b

    def reset(self):
        self.FrameOn = -1
        self.finished = False

# Module for posting data packets and containing app metadata
class Packet_posting:
    global Bitmapping
    Bitmapping = Bitmaps()

    def __init__(self,A = ""):
        try:
            self.corePropsPath = os.getenv('PROGRAMDATA') + "/SteelSeries/SteelSeries Engine 3/coreProps.json"
        except:
            raise FileNotFoundError('Steelseries Engine not found')
        self.sseAddress = json.load(open(self.corePropsPath))["address"]
        self.header = {"Content-Type":"application/json"}
        self.GameName = "REACTIVE_KEYBOARD_WIDGET"
        self.Name = "Keyboard_widget"
        self.Event = "KEY_UPDATE"
        self.ValueRange = 0

    def Start(self):
        # De-register the app
        metadata = {"game": self.GameName}
        r = self.Post(metadata, "/remove_game")
        # Re-register the app
        metadata = {"game": self.GameName, "game_display_name": self.Name}
        r = self.Post(metadata, "/game_metadata")
        # Define object handler and metadata
        metadata = {"game": self.GameName,
                    "event": self.Event,
                    "handlers": [{
                        "datas": [{
                            "has-text": False,
                            "image-data": Bitmapping.CompressBitmap(Bitmapping.CreateEmptyBitmap(128,40,0))}],
                        "device-type": "screened-128x40",
                        "mode": "screen",
                        "zone": "one"}]}
        # Register the event using metadata
        r = self.Post(metadata, "/bind_game_event")

    def Post(self, metadata, endpoint):
        try:
            r = requests.post("http://" + self.sseAddress + endpoint, json=metadata, headers=self.header)
            if r.status_code != 200:
                raise ConnectionError("Post status code returned as %s" % str(r.status_code))
            return r
        except Exception as e:
            raise ConnectionError(e)

    def value_lottery(self):
        if self.ValueRange == 100:
            self.ValueRange = 1
            return 100
        else:
            self.ValueRange += 1
            return self.ValueRange

global Posting
Posting = Packet_posting()

#Module for multithreading
class Work:

    def __init__(self, target):
        self.thread = threading.Thread(target=self.Timestamper, args=[target, target.__name__, self.FunctionClass(target)])
        self.thread.daemon = True
        self.thread.start()

    def Timestamper(self, target, funcname, funcclass):
        threadname = self.thread.name
        print("%s start: %s%s at %s" % (threadname,funcclass,funcname,time.ctime(time.time())))
        target()
        print("%s finished: %s%s ,  %s" % (threadname,funcclass,funcname,time.ctime(time.time())))

    def FunctionClass(self, method):
        method_name = method.__name__
        if method.__self__:
            classes = [method.__self__.__class__]
        else:
            # unbound method
            classes = [method.im_class]
        while classes:
            c = classes.pop()
            if method_name in c.__dict__:
                return "%s." % (P := str(c))[8:len(P)-2]
            else:
                classes = list(c.__bases__) + classes
        return ""