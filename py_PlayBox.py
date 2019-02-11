#!python.exe

import ctypes
from ctypes import *
import os
import sys
from time import sleep

class myMIDI:
    """MIDI関連関数コール処理用クラス"""
    def __init__(self, initData):
        if (sys.maxsize == 2 ** 63 - 1):
            self.initData = c_int64(initData)
            self.MIDI_MAPPER = c_int64(-1)
            self.h = c_uint64(0)
        else:
            self.initData = c_int32(initData)
            self.MIDI_MAPPER = c_int32(-1)
            self.h = c_uint32(0)
        
    def Init(self):
        ctypes.windll.Winmm.midiOutOpen(byref(self.h), self.MIDI_MAPPER, 0, 0, 0)
        ctypes.windll.winmm.midiOutShortMsg(self.h, self.initData)

    def Out(self, outData, length):
        ctypes.windll.winmm.midiOutShortMsg(self.h, outData)
        sleep(length/1000.0)

    def OutOnly(self, outData):
        #print('%x = %x' %(id(self.h), self.h))
        ctypes.windll.winmm.midiOutShortMsg(self.h, outData)

    def Close(self):
        ctypes.windll.winmm.midiOutReset(self.h)


class ScaleDefs:
    """音階定義を格納するクラス"""
    def __init__(self, scale, note):
        self.scale = scale
        self.note = note


class PlayData:
    """楽譜データを格納するクラス"""
    def __init__(self, scale, note, length):
        self.scale = scale
        self.note = note
        self.length = length


def loadDefFile(filename):
    """音階定義ファイルを読み込む"""

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

        temp = temp.replace(" ", "").replace("\t", "").rstrip()
        flds = temp.split("=")

        if temp != "":
            defs.append(ScaleDefs(flds[0],flds[1]))

    return defs


def loadPlayFile(filename):
    """楽譜ファイルを読み込む"""

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

        temp = temp.replace(" ", "").replace("\t", "").rstrip()
        flds = temp.split("=")

        if temp != "":
            pData.append(PlayData(flds[0], "", flds[1]))

    return pData


def replaceScalt_to_Freq(defs, pData):
    """音階文字列を検索し、ノートナンバーをセットする"""
    for currentData in pData:
        scale = currentData.scale.split(",")
        for temp in scale:
            for currentLen in defs:
                if temp == currentLen.scale:
                    if currentData.note == "":
                        currentData.note = currentLen.note
                    else:
                        currentData.note += "," + currentLen.note
                    break


def main():
    argv = sys.argv
    argc = len(argv)

    if (argc < 2):
        #引数の個数チェック
        print('Usage: python %s musicDataFile <timbre>' %argv[0] )
        quit()

    note_number_file = "note-number.dat"
    if not os.path.exists(note_number_file):
        print('%s not found.' %note_number_file)
        quit()

    if (argc >= 3):
            timbre = int(argv[2])
    else:
            timbre = 1

    # 音階定義ファイルの読み込み
    defs = loadDefFile(note_number_file)

    # 楽譜ファイルの読み込み
    pData = loadPlayFile(argv[1])

    # ノート番号のセット
    replaceScalt_to_Freq(defs, pData)

    initData = timbre*256 + 0xc0
    pm = myMIDI(initData)
    pm.Init()

    print("\nLoad Done. Play Start!!")

    i = 0
    for currentpData in pData:
        if currentpData.note != "":
            print('[%d] = %s( %s ), %s [ms]' %(i, currentpData.scale, currentpData.note, currentpData.length))
            cnote = currentpData.note.split(",")

            for data in cnote:
                # 鍵盤を押す
                play_on = "0x7f" + data + "90"
                pm.OutOnly(int(play_on, 16))

            sleep(int(currentpData.length) / 1000.0)

            for data in cnote:
                # 鍵盤を離す
                play_off = "0x7f" + data + "80"
                pm.OutOnly(int(play_off, 16))

        else:
            print('[%d] = rest, %s [ms]' %(i, currentpData.length))
            
            # 休符
            sleep(int(currentpData.length) / 1000.0)
        i += 1

    pm.Close()
    print()

if __name__ == "__main__":
    main()
