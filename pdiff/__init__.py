#!/usr/bin/env python3
"""Usage: cdiff dir1 dir2
Colors and simplifies the output of diff"""
import sys
import re
import os
from subprocess import Popen,PIPE
import glob
from termcolor import colored
from pdiff.accumulator import TextAccumulator
DEBUG = False
EXCLUDE = [".DS_Store",".saves","__pycache__"]
COLORS = {
    "": "white",
    "A": "red",
    "B": "cyan",
    "BOTH": "magenta",
    "BINARY": "yellow",
    "?": "yellow" #error
}

def out_line(lineno):
    """print line or lines depending on if singular or plural"""
    if "," in lineno:
        return f"lines {lineno.replace(',','-')}"
    return f"line {lineno}"
def simplify_path(path,dirs):
    """replace dir1 or dir2 with ==A== or ==B==, to shorten lines"""
    for ab in dirs: #pylint: disable=invalid-name
        if path.startswith(dirs[ab]):
            return path.replace(dirs[ab], f"«{ab}»",1)
    return path
def get_which(path, dirs):
    """from the directory name of path, determine which branch it is"""
    for ab in dirs: #pylint: disable=invalid-name
        if path.startswith(dirs[ab]): return ab
    return "?"


class MyAccumulator(TextAccumulator):
    """Adjusting TextAccumulator with cdiff specifics"""
    def __init__(self,dirs):
        super().__init__()
        self.infile = False
        self.dirs = dirs

    def filemode(self):
        """I am in a file"""
        self.infile = True
    def notfilemode(self):
        """I am not in a file. Print a line if I was last time"""
        if self.infile:
            self.line()
        self.infile = False

    def path(self, path):
        """Typeset a path with the appropriate color"""
        color = self.set_color(get_which(path,self.dirs))
        self.text += colored(simplify_path(path,self.dirs),color,attrs=["bold","underline"])


def main(dir1,dir2,*,brief=False,flags=""): #pylint: disable=too-many-locals
    """The main program"""
    #pylint: disable=invalid-name
    dirs = {"A": dir1, "B": dir2}
    result = MyAccumulator(dirs)
    result.colors = COLORS
    lines_A, lines_B = "",""
    dir_or_file = "FILE"
    def debug(mode):
        if DEBUG:
            AB = ""
            if lines_A: AB+="A"
            if lines_B: AB+="B"
            if result.infile: AB+="F"
            AB = f"[{AB}]"
            print(mode+": "+AB+" "+colored(line,"yellow"))

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
        f'diff -dr {flags} "{dir1}" "{dir2}" {exclude_string}',
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
            which = get_which(path,dirs)
            result.mode(f"ONLY {which} HAS THE FILE",which=which)
            result.path(path)

        elif M:=re.match(f"diff .* {dir1}/(.*) {dir2}/(.*)$",line):
            debug("STARTFILE")
            fileA,fileB = M.group(1),M.group(2)
            result.mode("FILES DIFFER")
            result.add(simplify_path(os.path.join(dir1,fileA),dirs),
                       which="A", endline=False)
            result.add(simplify_path(os.path.join(dir2,fileB),dirs),
                       which="B", endline=True)
            if not brief:
                result.filemode()

        elif line.startswith("<"): #from DIFF
            debug("in A")
            if not brief:
                if lines_A:
                    result.add(f"--in A {out_line(lines_A)}",
                               which="A",endline=True,bold=True)
                    lines_A = ""
                result.add(line[2:], which="A")


        elif line.startswith(">"):
            debug("in B")
            if not brief:
                if lines_B:
                    result.add(f"--in B {out_line(lines_B)}",which="B",endline=True,bold=True)
                    lines_B = ""
                result.add(line[2:], which="B")

        elif M:=re.match("([0-9,]*)c([0-9,]*)$",line):
            if not brief:
                debug("change")
                result.line("-",False)
                result.mode("text in A and B differ", which="BOTH", endline=True)
                lines_A = M.group(1)
                lines_B = M.group(2)

        elif M:=re.match("([0-9,]*)d([0-9,]*)$",line):
            if not brief:
                debug("only A")
                #result.mode("ONLY IN A",which="A")
                result.line("-",False)
                result.mode("text only in A", which="A")
                result.add(f"{out_line(M.group(1))}", endline=False)
                result.add(f"(compare {out_line(M.group(2))})", which="B", endline=True)


        elif M:=re.match("([0-9,]*)a([0-9,]*)$",line):
            if not brief:
                debug("only B")
                result.line("-",False)
                result.mode("text only in B",which="B")
                result.add(f"{out_line(M.group(2))}", endline=False)
                result.add(f"(compare {out_line(M.group(1))})", which="A", endline=True)
                result.startline()
                result.add(line)

    return result.text

def process_dir(arg):
    """Clean up the input"""
    path = arg
    path = glob.glob(arg) #pylint
    if not path:
        return ""
    return path[0].rstrip("/")

def process_args(args):
    """Process the line parameters"""
    flags = ""
    long_flags = []
    dirs = []
    for arg in args:
        if arg in ['--help','-h']:
            print("Help")
            sys.exit()
        if arg.startswith("--"):
            long_flags += [arg]
        elif arg.startswith("-") and "=" not in arg:
            flags += arg[1:]
        elif arg.startswith("-") and "=" in args:
            long_flags += [arg]
        else:
            dirs += [arg]
    if len(dirs) < 2:
        print("Usage: pdiff [flags] dir1 dir2")
        sys.exit()
    brief = False
    if "b" in flags:
        brief = True
        flags = flags.replace("b","")
    for letter in "qenylrdv":
        flags = flags.replace(letter,"")
    flagtext = " ".join(map(lambda x:"-"+x,flags))
    flagtext = " ".join(long_flags+[flagtext])
    d1 = process_dir(dirs[0]) #pylint: disable=invalid-name
    d2 = process_dir(dirs[1]) #pylint: disable=invalid-name
    try:
        print(main(d1, d2, brief=brief, flags=flagtext))
    except (BrokenPipeError,KeyboardInterrupt):
        print("--")

if __name__ == "__main__":
    process_args(sys.argv)
