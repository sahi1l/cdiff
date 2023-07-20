cdiff and qdiff are two command-line functions, which restyle the output of the "diff" function for easier reading when applied to directories.  

-`cdiff` shows all changes in the two directories recursively, including differences in individual files.
![example of cdiff output](doc/cdiff.png)
-`qdiff` (the q stands for "quick") only shows which files are different, in a much terser format.
![example of qdiff output](doc/qdiff.png)
Both use color to distinguish between elements from the two directories:
![red for the first directory, cyan for the second, magenta for both](doc/colorcode.png)
