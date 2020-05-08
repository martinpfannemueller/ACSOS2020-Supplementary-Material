# Evaluation 1 - SLOC

This folder contains the files used for creating die SLOC numbers. [cloc](https://github.com/AlDanial/cloc) using the language definition file `cloc_language_definitions` in this folder have been used. The language definition file is needed as cloc does not know about Acme, Clafer, and Stitch files.

## Reproducing the results

For the following you need to install cloc according to the instructions in the [repository](https://github.com/AlDanial/cloc).


### Rainbow

#### Table II

```
cloc --force-lang-def=cloc_language_definitions Rainbow/stitch/
       4 text files.
       4 unique files.
       1 file ignored.

github.com/AlDanial/cloc v 1.84  T=0.01 s (200.5 files/s, 14101.5 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Stitch                           2             18              0            113
YAML                             1              7             18             55
-------------------------------------------------------------------------------
SUM:                             3             25             18            168
-------------------------------------------------------------------------------
```

```
cloc --force-lang-def=cloc_language_definitions Rainbow/model/
       9 text files.
       9 unique files.
       6 files ignored.

github.com/AlDanial/cloc v 1.84  T=0.02 s (225.2 files/s, 30069.1 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
YAML                             1              7              3            261
ACME                             1             61              0            128
DTD                              1             13             25             25
XML                              1              0              0             11
-------------------------------------------------------------------------------
SUM:                             4             81             28            425
-------------------------------------------------------------------------------
```

#### Table III

```
cloc --force-lang-def=cloc_language_definitions Rainbow/system/
       9 text files.
       9 unique files.
       0 files ignored.

github.com/AlDanial/cloc v 1.84  T=0.02 s (435.0 files/s, 13051.0 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
YAML                             2              7              3             93
Perl                             2             28             14             91
Bourne Shell                     5             10              4             20
-------------------------------------------------------------------------------
SUM:                             9             45             21            204
-------------------------------------------------------------------------------
```


### REACT

#### Table II

```
cloc --force-lang-def=cloc_language_definitions REACT/SWIM-AOS.cfr
       1 text file.
       1 unique file.
       0 files ignored.

github.com/AlDanial/cloc v 1.84  T=0.01 s (91.8 files/s, 13316.4 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Clafer                           1             22              0            123
-------------------------------------------------------------------------------
```

```
cloc --force-lang-def=cloc_language_definitions REACT/SWIM-TSS.xml
       1 text file.
       1 unique file.
       0 files ignored.

github.com/AlDanial/cloc v 1.84  T=0.01 s (76.0 files/s, 2887.7 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
XML                              1              0              0             38
-------------------------------------------------------------------------------
```

#### Table III

```
cloc --force-lang-def=cloc_language_definitions REACT/SWIM_Interface.py
       1 text file.
       1 unique file.
       0 files ignored.

github.com/AlDanial/cloc v 1.84  T=0.02 s (59.5 files/s, 15005.2 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                           1             50              2            200
-------------------------------------------------------------------------------
```
