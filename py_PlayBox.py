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
## MIDI�֘A�֐��R�[�������p�N���X
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
## ���K��`���i�[����N���X
##-----------------------------------------------------------------##
class ScaleDefs:
  def __init__(self, scale, note):
    self.scale = scale
    self.note = note

##-----------------------------------------------------------------##
## �y���f�[�^���i�[����N���X
##-----------------------------------------------------------------##
class PlayData:
  def __init__(self, scale, note, length):
    self.scale = scale
    self.note = note
    self.length = length

##-----------------------------------------------------------------##
## ���K��`�t�@�C����ǂݍ���
##-----------------------------------------------------------------##
def loadDefFile(filename):
  # �t�@�C�����I�[�v������
  defFile = open(filename, "r")

  # �s���Ƃɂ��ׂēǂݍ���Ń��X�g�f�[�^�ɂ���
  lines = defFile.readlines()

  # �t�@�C�����N���[�Y����
  defFile.close()

  defs = []
  for temp in lines:
    pos = temp.find("//")

    # �R�����g�J�n����"//"���O�����o��
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
## ���K��`�t�@�C����ǂݍ���
##-----------------------------------------------------------------##
def loadPlayFile(filename):
  # �t�@�C�����I�[�v������
  playFile = open(filename, "r")

  # �s���Ƃɂ��ׂēǂݍ���Ń��X�g�f�[�^�ɂ���
  lines = playFile.readlines()

  # �t�@�C�����N���[�Y����
  playFile.close()

  pData = []
  for temp in lines:
    pos = temp.find("//")

    # �R�����g�J�n����"//"���O�����o��
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
## ���K��������������A�m�[�g�i���o�[���Z�b�g����
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
	#�����̌��`�F�b�N
	print('Usage: python %s musicDataFile <timbre>' %argv[0] )
	quit()

if (argc >= 3):
    timbre = int(argv[2])
else:
    timbre = 1

# ���K��`�t�@�C���̓ǂݍ���
defs = []
defs = loadDefFile("note-number.dat")

# �y���t�@�C���̓ǂݍ���
pData = []
pData = loadPlayFile(argv[1])

# �m�[�g�ԍ��̃Z�b�g
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
      # ���Ղ�����
      play_on = "0x7f" + data + "90"
      pm.OutOnly(int(play_on, 16))

    sleep(int(pData[i].length) / 1000)

    for data in cnote:
      # ���Ղ𗣂�
      play_off = "0x7f" + data + "80"
      pm.OutOnly(int(play_off, 16))

  else:
    print('[%d] = rest, %s [ms]' %(i, pData[i].length))
  i += 1

pm.Close()
print()
