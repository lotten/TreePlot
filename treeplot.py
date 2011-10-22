#!/usr/bin/python
""" TreePlot.py
by Lars Otten <lotten@ics.uci.edu>, 2011

Python script that plots a tree from a simple string representation
and outputs it to a SVG file. The output file name is the same as the
input with .svg attached.

The input file should follow the following simple grammar:
  T = ( <label> T* )

For instance:
  ( 0 ( 1 ( 2 ) ( 3 ) ) )
corresponds to this tree:

  0
  |
  1
 / \
2   3

See more examples (and their output) in the example/ folder.
"""

# Sets the radius and horizontal/vertical node distance for plotting.
NODE_RADIUS = 20
NODE_DIST_X = 50
NODE_DIST_Y = 60
# Node fill color
NODE_FILL = "#b0b0b0"
# Line width for plotting
LINE_WIDTH = 2


import sys
from pysvg.filter import *
from pysvg.gradient import *
from pysvg.linking import *
from pysvg.script import *
from pysvg.shape import *
from pysvg.structure import *
from pysvg.style import *
from pysvg.text import *
from pysvg.builders import *


class Node:
  """Implements a recursive tree structure."""

  def __init__(self, l):
    self.label = l
    self.children = []
    self.parent = None
    self.width = 1  # Max. width (in the plotting sense) of subtree
    self.height = None  # Number of tree levels below (incl. self)
    self.depth = None  # Number of tree levels above (excl. self)
    self.pos_x = None
    self.pos_y = None

  def __str__(self):
    return "Node %s with %i children" % (self.label,
                                         len(self.children))

  def add_child(self, child):
    self.children.append(child)
    child.parent = self

  def update_width(self):
    if len(self.children) == 0:
      self.width = 1
    else:
      self.width = sum([child.update_width()
                        for child in self.children])
    return self.width

  def update_depth(self, parent_depth = -1):
    self.depth = parent_depth + 1
    for child in self.children:
      child.update_depth(self.depth)

  def update_height(self):
    if len(self.children) == 0:
      self.height = 1
    else:
      self.height = 1 + max([child.update_height()
                             for child in self.children])
    return self.height


def compileTree(filename):
  """Simple parser to read the input file and generate the tree data
  structure. It's not bulletproof, but does the job."""

  f = open(filename, "r")
  content = f.read().strip()
  content = content.replace("("," ( ")
  content = content.replace(")", " ) ")
  T = content.split()

  # Just a few quick sanity checks.
  if T[0] != "(":
    print "Parsing error: Excepting '(' as first symbol."
    sys.exit(1)
  if len(T) < 3:
    print "Parsing error: Expecting at least one full node."
    sys.exit(1)

  root = Node(T[1])
  last = root
  depth = 1

  # Maintain a state to detect some malformed input.
  state = 1
  for i, t in enumerate(T[2:]):
    if t == ")" and (state == 1 or state == 2):
      depth -= 1
      last = last.parent
      state = 2
    elif t == "(" and (state == 1 or state == 2):
      depth += 1
      state = 0
    elif state == 0:
      node = Node(t)
      last.add_child(node)
      last = node
      state = 1
      #print node, depth
    else:
      print ("Parsing error: unexpected symbol '%s' at index %i"
             % (t, i+2))
      sys.exit(1)

  if depth != 0:
    print "Parsing error: Bracket mismatch."
    sys.exit(1)

  root.update_width()
  root.update_height()
  root.update_depth()
  return root


class TreePlotter:
  """Provides the tree plotting functionality through pySVG."""
  def __init__(self):
    self.indent = 0
    self.plot = svg()

    self.builder = ShapeBuilder()
    self.style_node = StyleBuilder()
    self.style_node.setFilling(NODE_FILL)
    self.style_node.setStroke("black")
    self.style_node.setStrokeWidth(LINE_WIDTH)

    self.style_text = StyleBuilder()
    self.style_text.setTextAnchor("middle")
    self.style_text.setDominantBaseline("central")

    self.style_line = StyleBuilder()
    self.style_line.setStroke("black")
    self.style_line.setStrokeWidth(LINE_WIDTH)
    
  def plotNode(self, node):
    """Adds a single node to the plot, incl. connection to parent."""
    # Compute node position
    pos_y = node.depth * NODE_DIST_Y
    pos_y += NODE_DIST_Y * 0.5
    pos_x = self.indent * NODE_DIST_X
    pos_x += node.width * NODE_DIST_X * 0.5
    node.pos_x = pos_x
    node.pos_y = pos_y

    # Actual node (circle)
    circle = self.builder.createCircle(pos_x, pos_y, NODE_RADIUS)
    circle.set_style(self.style_node.getStyle())
    self.plot.addElement(circle)

    # Node label
    T = text(node.label, pos_x, pos_y)
    T.set_style(self.style_text.getStyle())
    self.plot.addElement(T)

    # Connection to parent (if any)
    if node.parent:
      # Can use parent.pos_x/y since we're going depth-first.
      L = line(node.parent.pos_x, node.parent.pos_y + NODE_RADIUS,
               pos_x, pos_y - NODE_RADIUS)
      L.set_style(self.style_line.getStyle())
      self.plot.addElement(L)

  def plotTree(self, tree):
    """Go over nodes depth-first and add them to plot."""
    stack = [tree]
    while len(stack):
      node = stack.pop()
      stack.extend(node.children[::-1])
      self.plotNode(node)
      if len(node.children) == 0:
        self.indent += 1


def plot(filename):
  """Main plotting routine."""
  tree = compileTree(filename)
  plotter = TreePlotter()
  plotter.plotTree(tree)

  # For debugging:
  #print plotter.plot.getXML()
  plotter.plot.save(filename + ".svg")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Specify input file name"
    sys.exit(0)
  else:
    plot(sys.argv[1])

