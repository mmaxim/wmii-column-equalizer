#!/usr/bin/env python
#Mike Maxim mike@mmaxim.info

import os
import string
import sys

ScaleFactor = 11
Debug = False

def debug_out(s):
    global Debug
    if Debug:
        print s

class Window:
    def __init__(self, w):
        self.left = 0
        self.extent = 0
        self.name = 0
        self.desktop = 0
        self.fullname = ""

        self.parse(w)

    def parse(self, w):
        toks = string.split(w, ' ')
        wname = toks[0]
        self.left = int(toks[1])
        self.extent = int(toks[2])

        wtoks = string.split(wname, ':')
        self.fullname = wname
        if len(wtoks) == 1:
            self.desktop = 0
            self.name = int(wtoks[0])
        else:
            self.desktop = int(wtoks[0])
            self.name = int(wtoks[1])

    def to_string(self):
        s = "w: %d d: %d f: %s left: %d extent: %d" % (self.name, self.desktop,
                self.fullname, self.left, self.extent)
        return s

class Desktop:
    def __init__(self, id):
        self.windows = []
        self.windowhash = { }
        self.id = id

    def to_string(self):
        s = "Desktop: " + str(self.id) + "\n"
        for w in self.windows:
            s += w.to_string() + "\n"
        return s

    def get_total_width(self):
        my_width = 0.0
        for w in self.windows:
            my_width += w.extent
        return my_width

    def build_window_hash(self):
        for w in self.windows:
            self.windowhash[w.name] = w

    def resize_window(self, w, wright, des_size):
        global ScaleFactor

        delta_raw = des_size - w.extent
        delta = delta_raw / ScaleFactor

        debug_out("w: %s" % w.to_string())
        debug_out("delta_raw: %d delta: %d" % (delta_raw, delta))
        estr = "wmiir xwrite /tag/sel/ctl grow %s sel right %d" % (w.fullname, delta)
        debug_out("estr: %s" % estr)
        os.popen(estr)

        w.extent = des_size
        debug_out("new w: %s" % w.to_string())
        if wright:
            wright.left += delta_raw
            wright.extent -= delta_raw
            debug_out("new right: %s" % wright.to_string())
        debug_out("")

    def equalize(self):
        total_width = self.get_total_width()
        des_size = total_width / float(len(self.windows))

        debug_out("total_width: %d des_size: %d\n" % (total_width, des_size))
        self.build_window_hash()
        for w in self.windows:
            wright = self.windowhash.get(w.name+1)
            self.resize_window(w, wright, des_size)

def build_desktops(windows):

    desktops = { }
    for w in windows:
        if desktops.has_key(w.desktop):
            desktop = desktops[w.desktop]
            desktop.windows.append(w)
        else:
            d = Desktop(w.desktop)
            d.windows.append(w)
            desktops[w.desktop] = d

    return desktops.values()

def parse_windows(wlist):

    windows = []
    for w in wlist:
        windows.append(Window(w))

    return windows

def generate_windows():

    wlist = os.popen("wmiir read /tag/sel/index | grep \# | grep -v \~ | cut -c 3-").readlines()

    windows = parse_windows(wlist)
    desktops = build_desktops(windows)

    for d in desktops:
        debug_out(d.to_string())
        d.equalize()

def main():

    global Debug
    if len(sys.argv) == 2 and sys.argv[1] == "-d":
        Debug = True

    generate_windows()

if __name__ == "__main__":
    main()

