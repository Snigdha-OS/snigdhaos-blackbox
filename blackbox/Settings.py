#!/bin/python

import os
import Functions as fn
import string
from string import Template

# NOTE: Base Directory
base_dir = os.path.dirname(os.path.realpath(__file__))

# NOTE: Deafult Config File
default_file = "%s/defaults/blackbox.yaml"
