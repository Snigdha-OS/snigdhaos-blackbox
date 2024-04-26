#!/bin/python

import os
import subprocess
import queue
from queue import Queue
import sys
import time
from time import sleep
import signal

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

        if searchentry.get_text_length() == 0:
            self.search_activated = False

        search_term = searchentry.get_text()
        if not search_term.isspace():
            try:
                if len(search_term.rstrip().lstrip()) > 0:
                    th_search = fn.threading.Thread(
                        name="thread_search",
                        target=fn.search,
                        args=(
                            self,
                            search_term.rstrip().lstrip(),
                        ),
                    )
                    fn.logger.info("Starting search")
                    th_search.start()
                    # get the search_results from the queue
                    results = self.search_queue.get()
                    if results is not None:
                        fn.logger.info("Search complete")
                        if len(results) > 0:
                            total = 0
                            for val in results.values():
                                total += len(val)
                            fn.logger.info("Search found %s results" % total)
                            # make sure the gui search only displays the pkgs inside the results
                            GUI.setup_gui_search(
                                self,
                                Gtk,
                                Gdk,
                                GdkPixbuf,
                                base_dir,
                                os,
                                Pango,
                                results,
                                search_term,
                                None,
                            )
                            self.search_activated = True
                    else:
                        fn.logger.info("Search found %s results" % 0)
                        self.searchentry.grab_focus()
                        message_dialog = MessageDialog(
                            "Info",
                            "Search returned 0 results",
                            "Failed to find search term inside the package name or description.",
                            "Try to search again using another term",
                            "info",
                            False,
                        )
                        message_dialog.show_all()
                        message_dialog.run()
                        message_dialog.hide()
                elif self.search_activated == True:
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
            except Exception as err:
                fn.logger.error("Exception in on_search_activated(): %s" % err)
            finally:
                if self.search_activated == True:
                    self.search_queue.task_done()
    
    def on_search_cleared(self, searchentry, icon_pos, event):
        if self.search_activated:
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
        self.searchentry.set_placeholder_text("Search...")
        self.search_activated = False

    def on_close(self, widget, data):
        settings = Settings(self.display_versions, self.display_package_progress)
        settings.write_config_file()
        if os.path.exists(fn.blackbox_lockfile):
            os.unlink(fn.blackbox_lockfile)
        if os.path.exists(fn.blackbox_pidfile):
            os.unlink(fn.blackbox_pidfile)
        fn.terminate_pacman()
        Gtk.main_quit()
        print("")
        print("Thanks for using BlackBox")
        print("Report issues to make it even better")
        print("")
        print("")
        print("")

    def app_toggle(self, widget, active, package):
        if widget.get_state() == False and widget.get_active() == True:
            if len(package.name) > 0:
                inst_str = [
                    "pacman",
                    "-S",
                    package.name,
                    "--needed",
                    "--noconfirm",
                ]
                if self.display_package_progress is True:
                    if fn.check_pacman_lockfile():
                        widget.set_state(False)
                        widget.set_active(False)
                        proc = fn.get_pacman_process()
                        message_dialog = MessageDialog(
                            "Warning",
                            "Blackbox cannot proceed pacman lockfile found",
                            "Pacman cannot lock the db, a lockfile is found inside %s"
                            % fn.pacman_lockfile,
                            "Pacman is running: %s" % proc,
                            "warning",
                            False,
                        )
                        message_dialog.show_all()
                        message_dialog.run()
                        message_dialog.hide()
                        return True
                    else:
                        package_metadata = fn.get_package_information(package.name)
                        if (
                            type(package_metadata) is str
                            and package_metadata.strip()
                            == "error: package '%s' was not found" % package.name
                        ):
                            self.package_found = False
                            fn.logger.warning(
                                "The package %s was not found in any configured Pacman repositories"
                                % package.name
                            )
                            fn.logger.warning("Package install cannot continue")
                            message_dialog = MessageDialog(
                                "Error",
                                "Pacman repository error: package '%s' was not found"
                                % package.name,
                                "Blackbox cannot process the request",
                                "Are the correct pacman mirrorlists configured ?",
                                "error",
                                False,
                            )
                            message_dialog.show_all()
                            message_dialog.run()
                            message_dialog.hide()
                            widget.set_state(False)
                            widget.set_active(False)
                            return True
                        else:
                            widget.set_state(True)
                            widget.set_active(True)
                            progress_dialog = ProgressDialog(
                                "install",
                                package,
                                " ".join(inst_str),
                                package_metadata,
                            )
                            progress_dialog.show_all()
                            self.pkg_queue.put(
                                (
                                    package,
                                    "install",
                                    widget,
                                    inst_str,
                                    progress_dialog,
                                ),
                            )
                            th = fn.threading.Thread(
                                name="thread_pkginst",
                                target=fn.install,
                                args=(self,),
                                daemon=True,
                            )
                            th.start()
                            fn.logger.debug("Package-install thread started")
                else:
                    progress_dialog = None
                    widget.set_sensitive(False)
                widget.set_active(True)
                widget.set_state(True)
                fn.logger.info("Package to install : %s" % package.name)
                # another pacman transaction is running, add items to the holding queue
                if (
                    fn.check_pacman_lockfile() is True
                    and self.display_package_progress is False
                ):
                    self.pkg_holding_queue.put(
                        (
                            package,
                            "install",
                            widget,
                            inst_str,
                            progress_dialog,
                        ),
                    )
                    if fn.is_thread_alive("thread_check_holding_queue") is False:
                        th = fn.threading.Thread(
                            target=fn.check_holding_queue,
                            name="thread_check_holding_queue",
                            daemon=True,
                            args=(self,),
                        )
                        th.start()
                        fn.logger.debug("Check-holding-queue thread started")
                elif self.display_package_progress is False:
                    self.pkg_queue.put(
                        (
                            package,
                            "install",
                            widget,
                            inst_str,
                            progress_dialog,
                        ),
                    )
                    th = fn.threading.Thread(
                        name="thread_pkginst",
                        target=fn.install,
                        args=(self,),
                        daemon=True,
                    )
                    th.start()
                    fn.logger.debug("Package-install thread started")
        # switch widget is currently toggled on
        if widget.get_state() == True and widget.get_active() == False:
            # Uninstall the package
            if len(package.name) > 0:
                uninst_str = ["pacman", "-Rs", package.name, "--noconfirm"]
                fn.logger.info("Package to remove : %s" % package.name)
                if fn.check_pacman_lockfile():
                    widget.set_state(True)
                    widget.set_active(True)
                    fn.logger.info("Pacman lockfile found, uninstall aborted")
                    GLib.idle_add(
                        self.show_lockfile_message_dialog,
                        priority=GLib.PRIORITY_DEFAULT,
                    )
                    return True
                if self.display_package_progress is True:
                    package_metadata = fn.get_package_information(package.name)

                    progress_dialog = ProgressDialog(
                        "uninstall",
                        package,
                        " ".join(uninst_str),
                        package_metadata,
                    )
                    progress_dialog.show_all()
                else:
                    progress_dialog = None
                widget.set_active(False)
                widget.set_state(False)
                self.pkg_queue.put(
                    (
                        package,
                        "uninstall",
                        widget,
                        uninst_str,
                        progress_dialog,
                    ),
                )
                th = fn.threading.Thread(
                    name="thread_pkgrem",
                    target=fn.uninstall,
                    args=(self,),
                    daemon=True,
                )
                th.start()
                fn.logger.debug("Package-uninstall thread started")

        # fn.print_running_threads()

        # return True to prevent the default handler from running
        return True

        # App_Frame_GUI.GUI(self, Gtk, vboxStack1, fn, category, package_file)
        # widget.get_parent().get_parent().get_parent().get_parent().get_parent().get_parent().get_parent().queue_redraw()
        # self.gui.hide()
        # self.gui.queue_redraw()
        # self.gui.show_all()
    
    def show_lockfile_message_dialog(self):
        proc = fn.get_pacman_process()
        message_dialog = MessageDialog(
            "Warning",
            "Blackbox cannot proceed pacman lockfile found",
            "Pacman cannot lock the db, a lockfile is found inside %s"
            % fn.pacman_lockfile,
            "Process running = %s" % proc,
            "warning",
            False,
        )
        message_dialog.show_all()
        message_dialog.run()
        message_dialog.hide()
        message_dialog.destroy()