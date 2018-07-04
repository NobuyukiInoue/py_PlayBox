#!python.exe
# coding: cp932

import sys
from time import sleep
import ctypes
import numpy
from ctypes import *
#from ctypes.wintypes import DWORD
#from ctypes.wintypes import UINT

##-----------------------------------------------------------------##
## MIDI関連関数コール処理用クラス
##-----------------------------------------------------------------##
class myMIDI:
  def __init__(self, initData):
    self.initData = c_int32(initData)
    self.MIDI_MAPPER = c_int32(-1)
    self.h = c_uint32(0x00000000)
  
  def Init(self):
    ctypes.windll.Winmm.midiOutOpen(byref(self.h), self.MIDI_MAPPER, 0, 0, 0)
    ctypes.windll.winmm.midiOutShortMsg(self.h, initData)

  def Out(self, outData, length):
    ctypes.windll.winmm.midiOutShortMsg(self.h, outData)
    sleep(length/1000)

  def OutOnly(self, outData):
    #print('%x = %x' %(id(self.h), self.h))
    ctypes.windll.winmm.midiOutShortMsg(self.h, outData)

  def Close(self):
    ctypes.windll.winmm.midiOutReset(self.h)

##-----------------------------------------------------------------##
## 音階定義を格納するクラス
##-----------------------------------------------------------------##
class ScaleDefs:
  def __init__(self, scale, note):
    self.scale = scale
    self.note = note

##-----------------------------------------------------------------##
## 楽譜データを格納するクラス
##-----------------------------------------------------------------##
class PlayData:
  def __init__(self, scale, note, length):
    self.scale = scale
    self.note = note
    self.length = length

##-----------------------------------------------------------------##
## 音階定義ファイルを読み込む
##-----------------------------------------------------------------##
def loadDefFile(filename):
  # ファイルをオープンする
  defFile = open(filename, "r")

  # 行ごとにすべて読み込んでリストデータにする
  lines = defFile.readlines()

  # ファイルをクローズする
  defFile.close()

  defs = []
  for temp in lines:
    pos = temp.find("//")

    # コメント開始文字"//"より前を取り出す
    if (pos >= 0):
      temp = temp[:pos]

    temp = temp.replace(" ", "")
    temp = temp.replace("\t", "")
    temp = temp.rstrip()    # remove last \n
    flds = temp.split("=")

    if flds[0] != "":
      defs.append(ScaleDefs(flds[0],flds[1]))

  return defs

##-----------------------------------------------------------------##
## 音階定義ファイルを読み込む
##-----------------------------------------------------------------##
def loadPlayFile(filename):
  # ファイルをオープンする
  playFile = open(filename, "r")

  # 行ごとにすべて読み込んでリストデータにする
  lines = playFile.readlines()

  # ファイルをクローズする
  playFile.close()

  pData = []
  for temp in lines:
    pos = temp.find("//")

    # コメント開始文字"//"より前を取り出す
    if (pos >= 0):
      temp = temp[:pos]

    temp = temp.replace(" ", "")
    temp = temp.replace("\t", "")
    temp = temp.rstrip()    # remove last \n
    flds = temp.split("=")

    if flds[0] != "":
      pData.append(PlayData(flds[0], "", flds[1]))

  return pData

##--------------------------------------------------------##
## 音階文字列を検索し、ノートナンバーをセットする
##--------------------------------------------------------##
def replaceScalt_to_Freq(defs, pData):
  i = 0
  while i < len(pData):
    scale = pData[i].scale.split(",")
    for temp in scale:
      j = 0
      while j < len(defs):
        if temp == defs[j].scale:
          if pData[i].note == "":
            pData[i].note = defs[j].note
          else:
            pData[i].note += "," + defs[j].note
          break
        j += 1
    i += 1


##-----------------------------------------------------------------##
## Main
##-----------------------------------------------------------------##
argv = sys.argv
argc = len(argv)

if (argc < 2):
	#引数の個数チェック
	print('Usage: python %s musicDataFile <timbre>' %argv[0] )
	quit()

if (argc >= 3):
    timbre = int(argv[2])
else:
    timbre = 1

# 音階定義ファイルの読み込み
defs = []
defs = loadDefFile("note-number.dat")

# 楽譜ファイルの読み込み
pData = []
pData = loadPlayFile(argv[1])

# ノート番号のセット
replaceScalt_to_Freq(defs, pData)

initData = timbre*256 + 0xc0
pm = myMIDI(initData)
pm.Init()

print("")
print("Load Done. Play Start!!")

i = 0
while i < len(pData):
  if pData[i].note != "":
    print('[%d] = %s( %s ), %s [ms]' %(i, pData[i].scale, pData[i].note, pData[i].length))

    cnote = pData[i].note.split(",")

    for data in cnote:
      # 鍵盤を押す
      play_on = "0x7f" + data + "90"
      pm.OutOnly(int(play_on, 16))

    sleep(int(pData[i].length) / 1000)

    for data in cnote:
      # 鍵盤を離す
      play_off = "0x7f" + data + "80"
      pm.OutOnly(int(play_off, 16))

  else:
    print('[%d] = rest, %s [ms]' %(i, pData[i].length))
  i += 1

pm.Close()
print()
