#!/usr/bin/env python3
"""Usage: qdiff dir1 dir2
Calls diff on two directories and shows the names of files that are missing or that differ between the two
"""
import sys
import re
import os
import glob
from termcolor import colored as col
color1 = "red"
color2 = "cyan"
colorB = "magenta"
try:
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
except IndexError:
    print(f"Usage: {sys.argv[0]} <directory1> <directory2>")
    print("Color-coding and prefixes:")
    print(col("<File only exists in the first directory",color1))
    print(col(">File only exists in the second directory",color2))
    print(col("*File exists in both directories, in different forms",colorB))
    exit()

D1 = glob.glob(dir1)
D2 = glob.glob(dir2)
if not D1: print(f"File {dir1} not found.")
if not D2: print(f"File {dir2} not found.")
if (not D1) or (not D2): exit()
dir1 = D1[0].rstrip("/")
dir2 = D2[0].rstrip("/")
print("DIR1: ",col(dir1,color1))
print("DIR2: ",col(dir2,color2))
mode = ""
drawline = "="*80
def hilite_path(path):
    dir = os.path.dirname(path)
    base = os.path.basename(path)
    color = "white"
    if dir == dir1:
        dir = "A"
        color = color1
    elif dir == dir2:
        dir = "B"
        color = color2
    return col(dir+"/",color)+col(base,color,attrs=["bold","underline"])

inA = []
inB = []
inBoth = []
stream = os.popen(f"diff -x __pycache__ -x .saves -x .DS_Store -qr {dir1} {dir2}")
for line in stream:
    line=line.strip()
    color=""
    
    if M:=re.match(f"Files {dir1}/(.*) and {dir2}/(.*) differ",line):
        inBoth += [M.group(1)]
        print("* "+col(inBoth[-1],colorB))
        
    elif M:=re.match(f"Only in {dir1}/?(.*): (.*)$",line):
        inA += [M.group(1)+"/"+M.group(2)]
        print("< "+col(inA[-1],color1))

    elif M:=re.match(f"Only in {dir2}/?(.*): (.*)$",line):
        inB += [M.group(1)+"/"+M.group(2)]
        print("> "+col(inB[-1],color2))

    else:
        print(line)


#try:
#    for x in inA:
#        print(col(x,color1))
#    for x in inB:
#        print(col(x,color2))
#    for x in inBoth:
#        print(col(x,colorB))
#except KeyboardInterrupt:
#    print("--")
