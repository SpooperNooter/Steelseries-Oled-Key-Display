import time
import threading
import requests
import os
import json
from PIL import Image
import math
import trace

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
            if type(r) == type([]):
                r = Bitmap(FromBitmap=r)
            R = r.Copy()
            for e in R.bitmap:
                try:
                    e.index(2)
                    R = self.ClassInstance[self.Default].Return_base().Copy()
                    R.AlterBitmap(r)
                    break
                except: pass
            metadata = {"game": "REACTIVE_KEYBOARD_WIDGET",
                        "event": "KEY_UPDATE",
                        "data": {
                            "value": Posting.value_lottery(),
                            "frame": {
                                "image-data": R.CompressBitmap()
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
class Bitmap:

    def __init__(self, Width = None, Height = None, IntValue = 0, FromPng = None, FromBitmap = None):
        self.bitmap = None
        if Width != None and Height != None:
            self.bitmap = [[IntValue for e in range(Width)]for e in range(Height)]
        elif FromPng != None:
            if (a := os.path.splitext(FromPng)[1]) == ".png":
                a = list((Image.open(FromPng)).convert('RGBA').getdata())
                BitmapSize = Image.open(FromPng).size
                self.bitmap = [[round(sum(B[0:2]) / 765) if ShadingLevels[round((B := a[(i * BitmapSize[0]) + I])[3] / 25.5)][i][I] != 2 else 2 for I in range(BitmapSize[0])] for i in range(BitmapSize[1])]
            else:
                raise ImportError(f"File extension {a} not supported, only .png")
        elif FromBitmap != None:
            try:
                if FromBitmap.__class__.__init__ == "Bitmap" or "Frame":
                    self.bitmap = [[(I*1)for I in i]for i in FromBitmap.bitmap]
                else: self.bitmap = [[(I*1)for I in i]for i in FromBitmap]
            except: self.bitmap = [[(I*1)for I in i]for i in FromBitmap]
        else:
            raise SyntaxError("Not enough information to create bitmap")

    def Copy(self):
        return Bitmap(FromBitmap=[[(I*1)for I in i]for i in self.bitmap])

    def AlterBitmap(self, AlterationPacket, Offset=[0,0], Invert=False, FullAlter=False):
        try:
            if AlterationPacket.__class__.__name__ == "Bitmap" or "Frame":
                Alteration = AlterationPacket.bitmap
            else:
                raise SyntaxError("AlterationPacket cannot be a class")
        except: Alteration = AlterationPacket
        for e in range(len(Alteration)):
            for E in range(len(Alteration[e])):
                if (P := Alteration[e][E]) == 0 or P == 1 or FullAlter:
                    try:
                        self.bitmap[e + Offset[1]][E + Offset[0]] = ((1 if self.bitmap[e + Offset[1]][E + Offset[0]] == 0 else p) if Invert and p != 2 else p) if (p := Alteration[e][E]) == 1 or FullAlter else 0
                    except: break

    def CompressBitmap(self):
        CompletedBitmap = []
        CompressedByte = 0
        BitDigit = 8
        for a in self.bitmap:
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

    class Frame(Bitmap):
        def __init__(self,name,duration,bitmap):
            super().__init__(FromBitmap=bitmap)
            self.name = name
            self.duration = duration

    def __init__(self, *SpritePaths, RepeatOnFinished = False, RepeatIndex = -1):
        self.UsableFormats = {"": self.sliceAseDir, ".gif": self.sliceGIF}
        A = []
        for i in SpritePaths:
            try:
                A.append(self.UsableFormats[os.path.splitext(i)[1]](i))
            except SyntaxError:
                raise SyntaxError(f"Error loading file, path {i} likely contains escape sequences")
            except KeyError:
                raise KeyError(f"{os.path.splitext(i)[1]} is not a supported filetype")
        self.SpriteSet = [I for e in A for I in e]
        self.FrameOn = -1
        self.SpriteNumber = 0
        self.finished = False
        self.Repeat = RepeatOnFinished
        self.RepeatIndex = RepeatIndex
        a = 0
        for i in self.SpriteSet:
            a += i.duration
        self.Length = math.floor(a/(1000/ModuleManaging.FPS))

    def sliceGIF(self, filename):
        im = Image.open(filename)
        name = os.path.basename(filename)
        frames = im.n_frames
        Slices = []
        for z in range(frames):
            im.seek(z)
            rgb_im = im.convert('RGBA')
            G = list(rgb_im.getdata())
            a = self.Frame(f"{name}{z}", im.info['duration'], [[round(sum(B[:3])/765) if ShadingLevels[round((B:=G[(y*im.width)+x])[3]/25.5)][y][x] != 2 else 2 for x in range(im.width)]for y in range(im.height)])
            Slices.append(a)
        return Slices

    def sliceAseDir(self, DirPath):
        data = json.load(open(f"{DirPath}/info.json"))
        raw = list((Image.open(f"{DirPath}/sheet.png")).convert('RGBA').getdata())
        sheetSize = Image.open(f"{DirPath}/sheet.png").size
        Slices = [self.Frame(g, data["frames"][g]["duration"], [[round(sum(m[:3]) / 765) if ShadingLevels[round((m := raw[((data["frames"][g]["frame"]["y"] + i) * sheetSize[0]) + I + data["frames"][g]["frame"]["x"]])[3] / 25.5)][i][I] != 2 else 2 for I in range(data["frames"][g]["frame"]["w"])] for i in range(data["frames"][g]["frame"]["h"])]) for g in data["frames"]]
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
            b -= (i.duration/(1000/ModuleManaging.FPS))
            if b <= 0:
                self.SpriteNumber = self.SpriteSet.index(i)
                if i == self.SpriteSet[len(self.SpriteSet)-1]:
                    self.finished = True
                    if self.Repeat:
                        self.FrameOn = self.RepeatIndex
                else: self.finished = False
                return i
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
            b -= (i.duration/(1000/ModuleManaging.FPS))
            if b <= 0:
                self.SpriteNumber = self.SpriteSet.index(i)
                self.finished = i == self.SpriteSet[len(self.SpriteSet) - 1]
                return i
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
                            "image-data": Bitmap(128,40,0).CompressBitmap()}],
                        "device-type": "screened-128x40",
                        "mode": "screen",
                        "zone": "one"}]}
        # Register the event using metadata
        r = self.Post(metadata, "/bind_game_event")

    def Post(self, metadata, endpoint):
        try:
            r = requests.post("http://" + self.sseAddress + endpoint, json=metadata, headers=self.header)
            if r.status_code != 200:
                raise ConnectionError(f"Post status code for %s returned as %s" % str(endpoint),str(r.status_code))
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
        return None