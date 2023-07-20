#!/usr/bin/env python3
"""Text Accumulator"""
from termcolor import colored

class TextAccumulator:
    """Stores the output so it can be provided at once (though I don't know why?)"""
    def __init__(self):
        self.text = ""
        self.colors = {}
        self.curwhich = ""

    def startline(self):
        """Start a new line if one hasn't already been started"""
        if not (not self.text or self.text[-1]=="\n"):
            self.text += "\n"
        self.curwhich = "" #always reset

    def set_color(self,which=""):
        """Set the current color, or get it"""
        if which: self.curwhich = which
        if which in self.colors:
            return self.colors[which]
        return ""

    def add(self, val, *, which="", endline=True, bold=False):
        """Add val to the accumulator"""
        color = self.set_color(which)
        attrs = []
        if bold: attrs += ["bold"]
        self.text += f"{colored(val,color,attrs=attrs)} "
        if endline: self.startline()

    def line(self,char="=",longline=True):
        """Add a dashed line to the accumulator"""
        n = {True: 80, False: 40}[longline] #pylint: disable=invalid-name
        self.startline()
        self.text += char*n
        self.startline()


    def mode(self, text, which="",endline=False):
        """Typeset a header for the current line"""
        self.startline()
        #self.text += "\n"
        color = self.set_color(which)
        self.text += colored(text,color,attrs=["bold","underline"]) #FIX: just do mode here
        self.text += colored(": ",color)
        if endline: self.startline()
