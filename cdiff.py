#!/usr/bin/env python3
"""Usage: cdiff dir1 dir2"""
import os,sys
from termcolor import colored
exclude = [".ds_store",".saves",'.trash']
def inonly(A,B):
    lowerB = list(map(lambda x:x.lower(),B))
    return [a for a in A if a.lower() not in lowerB and a.lower() not in exclude]
def inboth(A,B):
    lowerB = list(map(lambda x:x.lower(),B))
    return [a for a in A if a.lower() in lowerB and a.lower() not in exclude]

def diff(rootA, rootB, dirname, lvl=0):
    """given two folders, return:
    - a list of files and directories which are in A but not B
    - a list of files and directories which are in B but not A
    - (a list of files in both that are different somehow)
    - a list of directories which are in both (for later perusal, or perhaps recursiveness now?)
    """
    _,dirsA,filesA = next(os.walk(os.path.join(rootA,dirname)))
    _,dirsB,filesB = next(os.walk(os.path.join(rootB,dirname)))
    onlyA = inonly(dirsA,dirsB) + inonly(filesA,filesB)
    onlyB = inonly(dirsB,dirsA) + inonly(filesB,filesA)
    onlyA = []
#    onlyA = [a for a in dirsA if a not in dirsB and a not in exclude] + [a for a in filesA if a not in filesB and a not in exclude]
#    onlyB = [a for a in dirsB if a not in dirsA and a not in exclude] + [a for a in filesB if a not in filesA and a not in exclude]
    bothdirs = inboth(dirsA,dirsB)
    #[a for a in dirsA if a in dirsB and a not in exclude]
    if not (onlyA or onlyB or bothdirs):
        return False
    if (onlyA or onlyB):
        print(colored(dirname,"white",attrs=["underline"])+"/") #, len(onlyA),len(onlyB),len(bothdirs))
    for x in sorted(onlyA):
        attr = ["underline"] if x in dirsA else []
        print(colored("A: "+os.path.basename(x),"red",attrs=attr))
    for x in sorted(onlyB):
        attr = ["underline"] if x in dirsB else []
        print(colored("B: "+os.path.basename(x),"cyan",attrs=attr))
    for x in sorted(bothdirs):
        diff(rootA, rootB, os.path.join(dirname,x), lvl+1)
    return True
#    return (onlyA, onlyB, bothdirs)



if __name__ == "__main__":
    root = "." if len(sys.argv)<=3 else sys.argv[3]
    diff(sys.argv[1],sys.argv[2],root)
