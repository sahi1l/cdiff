#!/usr/bin/env python3
"""Usage: cdiff dir1 dir2
Colors and simplifies the output of diff"""
import sys
import re
import os
from subprocess import Popen,PIPE
import glob
from termcolor import colored as col
DEBUG = False
BRIEF = False
EXCLUDE = [".DS_Store",".saves"]
COLORS = {
    "": "white",
    "A": "red",
    "B": "cyan",
    "BOTH": "magenta",
    "BINARY": "grey",
    "?": "yellow" #error
}

try:
    dir1 = sys.argv[1] #pylint: disable=invalid-name
    dir2 = sys.argv[2]
except IndexError:
    print(f"Usage: {sys.argv[0]} <directory1> <directory2>")
    sys.exit()

D1 = glob.glob(dir1)
D2 = glob.glob(dir2)
if not D1: print(f"File {dir1} not found.")
if not D2: print(f"File {dir2} not found.")
if (not D1) or (not D2): sys.exit()

dir1 = D1[0].rstrip("/")
dir2 = D2[0].rstrip("/")


def out_line(lineno):
    """print line or lines depending on if singular or plural"""
    if "," in lineno:
        return f"lines {lineno.replace(',','-')}"
    return f"line {lineno}"

def get_which(path):
    """from the directory name of path, determine which branch it is"""
    if path.startswith(dir1): return "A"
    if path.startswith(dir2): return "B"
    return "?"

def simplify_path(path):
    """replace dir1 or dir2 with ==A== or ==B==, to shorten lines"""
    if path.startswith(dir1):
        return path.replace(dir1, "«A»")
    if path.startswith(dir2):
        return path.replace(dir2, "«B»")
    return path

class TextAccumulator:
    """Stores the output so it can be provided at once (though I don't know why?)"""
    def __init__(self):
        self.text = ""
        self.colors = COLORS
        self.infile = False
        self.curwhich = "" #the current color of this line
    def filemode(self):
        """I am in a file"""
        self.infile = True
    def notfilemode(self):
        """I am not in a file. Print a line if I was last time"""
        if self.infile:
            self.line()
        self.infile = False
    def startline(self):
        """Start a new line if one hasn't already been started"""
        if not (not self.text or self.text[-1]=="\n"):
            self.text += "\n"
        self.curwhich = "" #always reset

    def set_color(self,which=""):
        """Set the current color, or get it"""
        if which: self.curwhich = which
        return self.colors[which]

    def add(self, val, *, which="", endline=True, bold=False):
        """Add val to the accumulator"""
        color = self.set_color(which)
        attrs = []
        if bold: attrs += ["bold"]
        self.text += f"{col(val,color,attrs=attrs)} "
        if endline: self.startline()

    def line(self,char="=",longline=True):
        """Add a dashed line to the accumulator"""
        n = {True: 80, False: 40}[longline] #pylint: disable=invalid-name
        self.startline()
        self.text += char*n
        self.startline()

    def path(self, path):
        """Typeset a path with the appropriate color"""
        color = self.set_color(get_which(path))
        self.text += col(simplify_path(path),color,attrs=["bold","underline"])

    def mode(self, text, which="",endline=False):
        """Typeset a header for the current line"""
        self.startline()
        #self.text += "\n"
        color = self.set_color(which)
        self.text += col(text,color,attrs=["bold","underline"]) #FIX: just do mode here
        self.text += col(": ",color)
        if endline: self.startline()


def main():
    """The main program"""
    #pylint: disable=invalid-name
    result = TextAccumulator()
    lines_A,lines_B = "",""
    dir_or_file = "FILE"
    def debug(mode):
        if DEBUG:
            AB = ""
            if lines_A: AB+="A"
            if lines_B: AB+="B"
            if result.infile: AB+="F"
            AB = f"[{AB}]"
            print(mode+": "+AB+" "+col(line,"yellow"))

    if os.path.isdir(dir1):
        dir_or_file = "DIR"
        #result.add("===COMPARING DIRECTORIES===", bold=True, endline=True)
    #else:
        #result.add("===COMPARING FILES===", bold=True, endline=True)
    result.add(f"{dir_or_file} «A»: {dir1}", which="A", bold=True, endline=True)
    result.add(f"{dir_or_file} «B»: {dir2}", which="B", bold=True, endline=True)
    result.line()
    exclude_string = ' '.join([f"-x {x}" for x in EXCLUDE])
    stream = Popen( #pylint: disable=consider-using-with
        #-d means find a smaller set of changes
        #-r means recursive
        f'diff -dr "{dir1}" "{dir2}" {exclude_string}',
        shell=True,stdout=PIPE).stdout
    #FIX: do I need shell?
    for line in stream:
        line=line.strip()
        try:
            line=line.decode()
        except UnicodeDecodeError:
            print(f"Error:{line}")
            continue

        if M:=re.match("Binary files (.*) and (.*) differ",line):
            debug("BINARY")
            result.notfilemode()
            fileA,fileB = M.group(1), M.group(2)
            #result.line()
            result.mode("BINARY",which="BINARY")
            result.path(fileA)
            result.add(" and ", endline=False)
            result.path(fileB)

        elif M:=re.match("Only in (.*): (.*)$",line):
            debug("ONEDIR")
            result.notfilemode()
            path = os.path.join(M.group(1),M.group(2))
            #result.line()
            which = get_which(path)
            result.mode(f"ONLY {which} HAS THE FILE",which=which)
            result.path(path)

        elif M:=re.match(f"diff .* {dir1}/(.*) {dir2}/(.*)$",line):
            debug("STARTFILE")
            fileA,fileB = M.group(1),M.group(2)
            result.mode("FILES DIFFER")
            result.add(simplify_path(os.path.join(dir1,fileA)),
                       which="A", endline=False)
            result.add(simplify_path(os.path.join(dir2,fileB)),
                       which="B", endline=True)
            result.filemode()

        elif line.startswith("<"): #from DIFF
            debug("in A")
            if lines_A:
                result.add(f"--in A {out_line(lines_A)}",which="A",endline=True,bold=True)
                lines_A = ""
            result.add(line[2:], which="A")

        elif line.startswith(">"):
            debug("in B")
            if lines_B:
                result.add(f"--in B {out_line(lines_B)}",which="B",endline=True,bold=True)
                lines_B = ""
            result.add(line[2:], which="B")

        elif M:=re.match("([0-9,]*)c([0-9,]*)$",line):
            debug("change")
            result.line("-",False)
            result.mode("text in A and B differ", which="BOTH", endline=True)
            lines_A = M.group(1)
            lines_B = M.group(2)
            #result.mode("CHANGE: ","magenta")
            #result.add(M.group(1), which="A", endline=False)
            #result.add(M.group(2), which="B", endline=True)

        elif M:=re.match("([0-9,]*)d([0-9,]*)$",line):
            debug("only A")
            #result.mode("ONLY IN A",which="A")
            result.line("-",False)
            result.mode("text only in A", which="A")
            result.add(f"{out_line(M.group(1))}", endline=False)
            result.add(f"(compare {out_line(M.group(2))})", which="B", endline=True)

        elif M:=re.match("([0-9,]*)a([0-9,]*)$",line):
            debug("only B")
            result.line("-",False)
            result.mode("text only in B",which="B")
            result.add(f"{out_line(M.group(2))}", endline=False)
            result.add(f"(compare {out_line(M.group(1))})", which="A", endline=True)
            result.startline()
            result.add(line)
    return result

try:
    print(main().text)
except (BrokenPipeError,KeyboardInterrupt):
    print("--")
