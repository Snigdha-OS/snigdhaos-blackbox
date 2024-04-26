#!/bin/python

import os
import subprocess
import queue
from queue import Queue
# UI modules
from ui.GUI import GUI
from ui.SplashScreen import SplashScreen
from ui.ProgressBarWindow import ProgressBarWindow
from ui.AppFrameGUI import AppFrameGUI
from ui.AboutDialog import AboutDialog
from ui.MessageDialog import MessageDialog
from ui.PacmanLogWindow import PacmanLogWindow
from ui.PackageListDialog import PackageListDialog
from ui.ProgressDialog import ProgressDialog
# from ui.ISOPackagesWindow import ISOPackagesWindow
from ui.PackageSearchWindow import PackageSearchWindow
from ui.PackagesImportDialog import PackagesImportDialog

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import Functions as fn

base_dir = os.path.dirname(os.path.realpath(__file__))

class Main(Gtk.Window): # Basic OOPS Concept
    queue = Queue()
    pkg_queue = Queue()
    search_queue = Queue()
    pacmanlog_queue = Queue()
    pkg_holding_queue = Queue()

    def __init__(self):
        try:
            super(Main, self).__init__(title="BlackBox")
            self.set_border_width(10)
            self.connect("delete-event", self.on_close)
            self.set_position(Gtk.WindowPosition.CENTER) # DOCS : https://docs.gtk.org/gtk3/enum.WindowPosition.html
            self.set_icon_from_file(os.path.join(base_dir, "images/blackbox.png"))
            self.set_default_size(1280, 720) # Basic Con
            # let's give a focus on search entry * set "ctrl + f"
            self.connect("key-press-event", self.key_press_event)
            self.timeout_id = None
            self.display_version = False # Bool

            self.search_activated = False
            
