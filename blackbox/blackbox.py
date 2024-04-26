#!/bin/python

import os
import subprocess
import queue
from queue import Queue
import sys
import time
from time import sleep
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
from gi.repository import Gtk,Gdk,GdkPixbuf, Pango, GLib

import Functions as fn
from Settings import Settings
from requests.packages import package

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
            self.display_package_progress = False
            print("******************************************************")
            print(" Report error:")
            print("******************************************************")
            print("")
            print("******************************************************")
            if os.path.exists(fn.blackbox_lockfile):
                running = fn.check_if_process_running("blackbox")
                if running is True:
                    fn.logger.error(
                        "BlackBox LockFile (%s) Found!🫠" % fn.blackbox_lockfile
                    )
                    fn.logger.error(
                        "Another BlackBox instance Running already?"
                    )
                    sys.exit(1)
            else:
                splash_screen = SplashScreen()
                while Gtk.events_pending(): # DOCS: https://docs.gtk.org/gtk3/func.events_pending.html
                    Gtk.main_iteration()
                sleep(1.5)
                splash_screen.destroy()
                if fn.check_pacman_lockfile():
                    message_dialog = MessageDialog(
                        "Error",
                        "Blackbox failed to initiate, Pacman Lockfile Found!",
                        "Pacman unable to lock the database!" % fn. pacman_lockfile,
                        "Is another process running?",
                        "error",
                        False,
                    )
                    message_dialog.show_all()
                    message_dialog.run()
                    message_dialog.hide()
                    sys.exit(1)
                fn.logger.info(
                    "pkgver = pkgversion"
                )
                fn.logger.info(
                    "pkgrel = pkgrelease"
                )
                print("*************************************************")
                fn.logger.info("Distro = " + fn.distr)
                print("*************************************************")
                if os.path.isdir(fn.home + "/.config/gtk-3.0"):
                    try:
                        if not os.path.islink("/root/.config/gtk-3.0"):
                            if os.path.exists("/root/.config/gtk-3.0"):
                                fn.shutil.rmtree("/root/.config/gtk-3.0")
                            fn.shutil.copytree(
                                fn.home + "/.config/gtk-3.0", "/root/.config/gtk-3.0"
                            )
                    except Exception as e:
                        fn.logger.warning(
                            "GTK Config: %s" % e
                        )
                # if os.path.isdir
                fn.logger.info(
                    "Storing package metadate started."
                )
                self.packages = fn.store_packages()
                fn.logger.info(
                    "Storing packages metadat completed."
                )
                fn.logger.info(
                    "categories: %s" % len(self.packages.keys())
                )
                total_packages = 0
                for category in self.packages:
                    total_packages += len(self.packages[category])
                fn.logger.info(
                    "Total Packages: %s" % total_packages
                )
                fn.logger.info(
                    "Initiating GUI"
                )
                GUI.setup_gui(
                    self,
                    Gtk,
                    Gdk,
                    GdkPixbuf,
                    base_dir,
                    os,
                    Pango,
                    fn.settings_config,
                )
                fn.get_current_installed()
                installed_lst_file = "%s/cache/installed.lst" % base_dir
                packages_app_start_file = "%s/%s-packages.txt" % (
                    fn.log_dir,
                    fn.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                )
                if os.path.exists(installed_lst_file):
                    fn.logger.info(
                        "Created installed.lst"
                    )
                thread_pacman_sync_db = fn.threading.Thread(
                    name="thread_pacman_sync_db",
                    target=self.pacman_db_sync,
                    daemon=True,
                )
                thread_pacman_sync_db.start()
        except Exception as e:
            fn.logger.error(
                "Found Exception in Main(): %s" % e
            )
    
    def pacman_db_sync(self):
        sync_err = fn.sync_package_db()
        if sync_err is not None:
            fn.logger.error(
                "Pacman Database Synchronization Faild!"
            )
            print("--")
            GLib.idle_add(
                self.show_sync_db_message_dialog,
                sync_err,
                priority=GLib.PRIORITY_DEFAULT,
            )
        else:
            fn.logger.info(
                "Pacman Dtabase Synchronization Completed."
            )
            return True
    
    def show_sync_db_message_dialog(self, sync_err):
        message_dialog = MessageDialog(
            "Error",
            "Pacman db Synchronization faled!",
            "Failed to run command: sudo pacman -Sy\nPacman db synchronization failed.\nCheck pcman sync log",
            sync_err,
            "error",
            True,
        )
        message_dialog.show_all()
        message_dialog.run()
        message_dialog.hide()
    
    def on_keypress_event(self, widget, event):
        shortcut = Gtk.accelerator_get_label(event.keyval, event.state)
        if shortcut in ("Ctrl+F", "Ctrl+Mod2+F"):
            self.searchentry.grab_focus()
        if shortcut in ("Ctrl+I", "Ctrl+Mod2+I"):
            fn.show_package_info(self)

    def on_search_activated(self, searchentry):
        if searchentry.get_text_length() == 0 and self.search_activated:
            GUI.setup_gui(
                self,
                Gtk,
                Gdk,
                GdkPixbuf,
                base_dir,
                os,
                Pango,
                None,
            )
            self.search_activated = False

    
