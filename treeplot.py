#!/usr/bin/python
""" TreePlot.py
by Lars Otten <lotten@ics.uci.edu>, 2011

Python script that generates an SVG tree plot from a simple
string representation.
"""

import sys


def plotTree(filename):
    """Main plotting routine."""
    pass

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Specify input file name"
    sys.exit(0)
  else:
    plotTree(sys.argv[1])

