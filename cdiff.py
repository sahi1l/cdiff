#!/usr/bin/env python3
"""Usage: cdiff dir1 dir2
Colors and simplifies the output of diff"""
import sys
import re
import os
from subprocess import Popen,PIPE
import glob
from termcolor import colored as col
binary_color="grey"
drawline = "="*80
exclude = [".DS_Store",".saves"]
try:
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
except IndexError:
    print(f"Usage: {sys.argv[0]} <directory1> <directory2>")
    exit()

D1 = glob.glob(dir1)
D2 = glob.glob(dir2)
if not D1: print(f"File {dir1} not found.")
if not D2: print(f"File {dir2} not found.")
if (not D1) or (not D2): exit()

dir1 = D1[0].rstrip("/")
dir2 = D2[0].rstrip("/")
color1 = "red"
color2 = "cyan"
result = []
print(col(f"A: {dir1}",color1,attrs=["bold"]))
print(col(f"B: {dir2}",color2,attrs=["bold"]))

def print_list(*args):
    global result
    result += [' '.join(args)]
def mode(txt,color="white"):
    return col(txt,color,attrs=["bold"])

def hilite_path(path):
    dir = os.path.dirname(path)
    base = os.path.basename(path)
    error = ""
    color = "white"
    if dir.startswith(dir1):
        dir=dir.replace(dir1,"A")
        color = color1
    elif dir.startswith(dir2):
        dir=dir.replace(dir2,"B")
        color = color2
    else:
        print(f"{dir=},{dir1=},{dir2=}")
        dir = "?"
    return col(dir+"/",color)+col(base,color,attrs=["bold","underline"])
                
#stream = Popen(["diff","-r",dir1,dir2],stdout=PIPE,stderr=PIPE).communicate()[0]
#stream = os.popen(f'diff -r "{dir1}" "{dir2}"')
exclude_string = ' '.join([f"-x {x}" for x in exclude])
stream = Popen(f'diff -r "{dir1}" "{dir2}" {exclude_string}',shell=True,stdout=PIPE).stdout
for line in stream:
    line=line.strip()
    color=""
    try:
        line=line.decode()
    except UnicodeDecodeError:
        print(f"Error:{line}")
        continue
    if M:=re.match("Binary files (.*) and (.*) differ",line):
        print_list(drawline)
        print_list(mode("BINARY: "),
              hilite_path(M.group(1)),
              " and ",
              hilite_path(M.group(2)))
        
    elif M:=re.match("Only in (.*): (.*)$",line):
        print_list(drawline)
        print_list(mode("ONLY IN: "),
              hilite_path(M.group(1).rstrip("/")+"/"+M.group(2)))

    elif M:=re.match(f"diff -r .* {dir1}/(.*) {dir2}/(.*)$",line):
        print_list(drawline)
        print_list(mode("DIFF: "),
              col(M.group(1),color1),
              col(M.group(2),color2))
        
    elif line.startswith("<"):
        print_list(col(line[2:],color1))
    elif line.startswith(">"):
        print_list(col(line[2:],color2))
    elif M:=re.match("([0-9,]*)d([0-9,]*)$",line):
        print_list(mode("\nDELETE: ",color1),col(f"{M.group(1)} {M.group(2)}",color1))
    elif M:=re.match("([0-9,]*)c([0-9,]*)$",line):
        print_list(mode("\nCHANGE: ","magenta"),col(f"{M.group(1)} {M.group(2)}","magenta"))
    elif M:=re.match("([0-9,]*)a([0-9,]*)$",line):
        print_list(mode("\nADD: ",color2),col(f"{M.group(1)} {M.group(2)}",color2))
        
    else:
        print_list(line)

try:
    for line in result:
        print(line)
except (BrokenPipeError,KeyboardInterrupt):
    print("--")
    exit
