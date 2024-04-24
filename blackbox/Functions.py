#!/bin/python

import os
from os import makedirs
import sys
import psutil
import gi
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
from threading import Thread
import datetime
from datetime import datetime
from datetime import timedelta
from datetime import time
import shutil
import Functions as fn

from Settings import Settings
from Package import Package
from ui.MessageDialog import MessageDialog


gi.require_version("Gtk" "3.0") # GTK 2.0 is dead!
from gi.repository import GLib, Gtk

# NOTE: Base Directory
base_dir = os.path.dirname(os.path.realpath(__file__))

# NOTE: Global Variables 
sudo_username = os.getlogin()
home = "/home/" + str(sudo_username)
path_dir_cache = base_dir + "/cache/"
packages = []
distr = id()
blackbox_lockfile = "/tmp/blackbox.lock"
blackbox_pidfile = "/tmp/blackbox.pid"
process_timeout = 300 # NOTE: process time out has been set to 5 mins.
snigdhaos_mirrorlist = "/etc/pacman.d/snigdhaos-mirrorlist"

# NOTE: pacman settings
pacman_conf = "/etc/pacman.conf"
pacman_conf_backup = "/etc/pacman.conf.bak" # NOTE: Bak stands for backup
pacman_logfile = "/var/log/pacman.log"
pacman_lockfile = "/var/lib/pacman/db.lck"
pacman_cache_dir = "/var/cache/pacman/pkg/"

# NOTE: Snigdha OS Mirror Config
snigdhaos_core = [
    "[snigdhaos-core]"
    "SigLevel = PackageRequired DatabaseNever"
    "Include = /etc/pacman.d/snigdhaos-mirrorlist"
]
snigdhaos_extra = [
    "[snigdhaos-extra]"
    "SigLevel = PackageRequired DatabaseNever"
    "Include = /etc/pacman.d/snigdhaos-mirrorlist"
]

# NOTE: BlackBox Specific
log_dir = "/var/log/blackbox/"
config_dir = "%s/.config/blackbox" % home
config_file = "%s/blackbox.yaml" % config_dir # NOTE: It is already on $pwd
event_log_file = "%s/event.log" % log_dir
export_dir = "%s/blackbox-exports" % home

# NOTE: Permissions specified here

def permissions(dst):
    try:
        # NOTE : Use try-catch block so that we can trace any error!
        groups = subprocess.run(
            ["sh", "-c", "id " + sudo_username],
            shell=False,
            stdout=subprocess.PIPE, # NOTE: Standard Output
            stderr=subprocess.STDOUT, # NOTE: Standard Error Output
        )
        for i in groups.stdout.decode().split(" "):
            if "gid" in i:
                g = i.split("(")[1]
                group = g.replace(")", "").strip() # NOTE: replace with nothing!
        subprocess.call(["chown", "-R", sudo_username + ":" + group, dst], shell=False)
    except Exception as e:
        logger.error(e)

# NOTE: Creating Log, Export and Config Directory:
try:
    if not os.path.exists(log_dir):
        makedirs(log_dir)
    if not os.path.exists(export_dir):
        makedirs(export_dir)
    if not os.path.exists(config_dir):
        makedirs(config_dir)
    
    permissions(export_dir)
    permissions(config_dir)

    print("[INFO] Log Directory: %s" % log_dir)
    print("[INFO] Export Directory: %s" % export_dir)
    print("[INFO] Config Directory: %s" % config_dir)

except os.error as oserror:
    print("[ERROR] Exception: %s" % oserror)
    sys.exit(1)

# NOTE: Read Config File dst: $HOME/.config/blackbox/blackbox.yaml
# NOTE: Initiate logger
try:
    settings = Settings(False, False)
    settings_config = settings.read_config_file()
    logger = logging.getLogger("logger")
    # NOTE: Create a console handler
    ch = logging.StreamHandler()
    # NOTE: Rotate the fucking event log!
    tfh = TimedRotatingFileHandler(
        event_log_file,
        encoding="UTF-8",
        delay=False,
        when="W4",
    )

    if settings_config:
        debug_logging_enabled = None
        debug_logging_enabled = settings_config[
            "Debug Logging"
        ]

        if debug_logging_enabled is not None and debug_logging_enabled is True:
            logger.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
            tfh.setLevel(level=logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            ch.setLevel(logging.INFO)
            tfh.setLevel(level=logging.INFO)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
        tfh.setLevel(level=logging.INFO)
    # NOTE: Docs -> https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s > %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    # NOTE :  Call formatter to ch & tfh
    ch.setFormatter(formatter)
    tfh.setFormatter(formatter)
    # NOTE: Append ch to logger
    logger.addHandler(ch)
    # NOTE: Append File Handler to logger
    logger.addHandler(tfh)

except Exception as e:
    print("[ERROR] Failed: %s" % e)

# NOTE : On app close create package file 
def _on_close_create_package_file():
    try:
        logger.info("App cloding saving currently installed package to file")
        package_file = "%s-packages.txt" % datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logger.info("Saving: %s%s" %(log_dir, package_file))
        cmd = [
            "pacman",
            "-Q",
        ]
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as process:
            with open("%s/%s" % (log_dir, package_file), "w") as f:
                for line in process.stdout:
                    f.write("%s" %line)
    except Exception as e:
        logger.error("[ERROR] Exception: %s" % e)
        
# NOTE: Global Functions

def _get_position(lists, value):
    data = [
        string for string in lists if value in string
    ]
    position = lists.index(data[0])
    return position

def is_file_stale(filepath, stale_days, stale_hours, stale_minutes):
    now = datetime.now()
    stale_datetime = now - timedelta(
        days=stale_days,
        hours=stale_hours,
        minutes=stale_minutes,
    )
    if os.path.exists(filepath):
        file_created = datetime.fromtimestamp(
            os.path.getctime(filepath)
        )
        if file_created < stale_datetime:
            return True
    else:
        return False
    
# NOTE : Pacman
def sync_package_db():
    try:
        sync_str = [
            "pacman",
            "-Sy",
        ]
        logger.info(
            "Synchronizing Package Database..."
        )
        process_sync = subprocess.run(
            sync_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,
        )
        if process_sync.returncode == 0:
            return None
        else:
            if process_sync.stdout:
                out = str(process_sync.stdout.decode("UTF-8"))
                logger.error(out)
                return out
    except Exception as e:
        logger.error(
            "[ERROR] Exception: %s" % e
        )

def sync_file_db():
    try:
        sync_str = [
            "pacman",
            "-Fy",
        ]
        logger.info(
            "Synchronizing File Database..."
        )
        process_sync = subprocess.run(
            sync_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,

        )
        if process_sync.returncode == 0:
            return None
        else:
            if process_sync.stdout:
                out = str(process_sync.stdout.decode("UTF-8"))
                logger.error(out)
                return out
    except Exception as e:
        logger.error(
            "[ERROR] Exception: %s" % e
        )

# NOTE: Installation & Uninstallation Process
def start_subprocess(
        self,
        cmd,
        progress_dialog,
        action,
        pkg,
        widget
):
    try:
        self.switch_package_version.set_sensitive(False)
        self.switch_snigdhaos_keyring.set_sensitive(False)
        self.switch_snigdhaos_mirrorlist.set_sensitive(False)

        widget.set_sensitive(False)

        process_stdout_lst = []
        process_stdout_lst.append(
            "Command = %s\n\n" % " ".join(cmd)
        )
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as process:
            if progress_dialog is not None:
                progress_dialog.pkg_dialog_closed = False
            self.in_progress = True
            if (
                progress_dialog is not None and progress_dialog.pkg_dialog_closed is False
            ):
                line = (
                    "Pacman Processing: %s Package: %s \n\n Command: %s\n\n" % (action, pkg.name, " ".join(cmd))
                )
                # DOC: https://docs.gtk.org/glib/const.PRIORITY_DEFAULT.html
                GLib.idle_add(
                    update_progress_textview,
                    self,
                    line,
                    progress_dialog,
                    priority=GLib.PRIORITY_DEFAULT,
                )
            logger.debug("Pacman is processing the request.")

            while True:
                if process.poll() is not None:
                    break
                if (
                    progress_dialog is not None and progress_dialog.pkg_dialog_closed is False
                ):
                    for line in process.stdout:
                        GLib.idle_add(
                            update_progress_textview,
                            self,
                            line,
                            progress_dialog,
                            priority=GLib.PRIORITY_DEFAULT,
                        )
                        process_stdout_lst.append(line)
                    time.sleep(0.3)
                else:
                    for line in process.stdout:
                        process_stdout_lst.append(line)
                    time.sleep(1)
            returncode = None
            returncode = process.poll()

            if returncode is not None:
                logger.info(
                    "Pacman process completion: %s" % " ".join(cmd)
                )
                GLib.idle_add(
                    refresh_ui,
                    self,
                    action,
                    widget,
                    pkg,
                    progress_dialog,
                    process_stdout_lst,
                    priority=GLib.PRIORITY_DEFAULT,
                )
            else:
                logger.error(
                    "Pacman process failed to run %s" % " ".join(cmd)
                )

    except TimeoutError as terr:
        # print(e)
        logger.error(
            "Timeout Error in %s : %s" % (action, terr)
        )
        process.terminate()
        if progress_dialog is not None:
            progress_dialog.btn_package_progress_close.set_sensitive(True)
        self.switch_package_version.set_sensitive(True)
        self.switch_snigdhaos_keyring.set_sensitive(True)
        self.switch_snigdhaos_mirrorlist.set_sensitive(True)
    
    except SystemError as syerr:
        logger.error(
            "Timeout Error in %s : %s" % (action, syerr)
        )
        process.terminate()
        if progress_dialog is not None:
            progress_dialog.btn_package_progress_close.set_sensitive(True)
        self.switch_package_version.set_sensitive(True)
        self.switch_snigdhaos_keyring.set_sensitive(True)
        self.switch_snigdhaos_mirrorlist.set_sensitive(True)

def refresh_ui(
        self,
        action,
        switch,
        pkg,
        progress_dialog,
        process_stdout_lst,
):
    self.switch_package_version.set_sensitive(False)
    self.switch_snigdhaos_keyring.set_sensitive(False)
    self.switch_snigdhaos_mirrorlist.set_sensitive(False)  

    logger.debug("Checking if the package installed..." % pkg.name)
    installed = check_package_installed(pkg.name)
    if progress_dialog is not None:
        progress_dialog.btn_package_progress_close.set_sentitive(True)
    if installed is True and action == "install":
        logger.debug("Toggle switch state = True")
        switch.set_sensitive(True)
        switch.set_state(True)
        switch.set_active(True)
        if progress_dialog is not None:
            if progress_dialog.pkg_dialog_closed is False:
                progress_dialog.set_title(
                    "Package installed: %s" % pkg.name
                )
                progress_dialog.infobar.set_name(
                    "infobar_info"
                )
                content = progress_dialog.infobar.get_content_area()
                if content is not None:
                    for widget in content.get_children():
                        content.remove(widget)
                    # DOCS: https://docs.gtk.org/gtk3/class.Label.html
                    lbl_install = Gtk.Label(xalign=0, yalign=0)
                    # DOCS: https://stackoverflow.com/questions/40072104/multi-color-text-in-one-gtk-label
                    lbl_install.set_markup(
                        "<b>Package %s installed.</b>" % pkg.name
                    )
                    content.add(lbl_install)
                    if self.timeout_id is not None:
                        # DOCS: https://gtk-rs.org/gtk-rs-core/stable/0.14/docs/glib/source/fn.source_remove.html
                        GLib.source_remove(self.timeout_id)
                        self.timeout_id = None
                    self.timeout_id = GLib.timeout_add(
                        100,
                        reveal_infobar,
                        self,
                        progress_dialog,
                    )
    if installed is False and action == "install":
        logger.debug("Toggle switch state = False")
        if progress_dialog is not None:
            switch.set_sensitive(True)
            switch.set_state(False)
            switch.set_active(False)
            if progress_dialog.pkg_dialog_closed is False:
                progress_dialog.set_title("%s install failed" % pkg.name)
                progress_dialog.infobar.set_name("infobar_error")
                content = progress_dialog.infobar.get_content_area()
                if content is not None:
                    for widget in content.get_children():
                        content.remove(widget)
                    lbl_install = Gtk.Label(xalign=0, yalign=0) 
                    lbl_install.set_markup(
                        "<b>Package %s installed failed.</b>" % pkg.name
                    )
                    content.add(lbl_install)
                    if self.timeout_id is not None:
                        # DOCS: https://gtk-rs.org/gtk-rs-core/stable/0.14/docs/glib/source/fn.source_remove.html
                        GLib.source_remove(self.timeout_id)
                        self.timeout_id = None
                    self.timeout_id = GLib.timeout_add(
                        100,
                        reveal_infobar,
                        self,
                        progress_dialog,
                    )
            else:
                logger.debug(" ".join(process_stdout_lst))
                message_dialog = MessageDialog(
                    "Errors occured suring installation",
                    "Errors occured during installation of %s failed" % pkg.name,
                    "Pacman failed to install %s" %pkg.name,
                    " ".join(process_stdout_lst),
                    "error",
                    True,
                )
                message_dialog.show_all()
                result = message_dialog.run()
                message_dialog.destroy()
        elif progress_dialog is None or progress_dialog.pkg_dialog_closed is True:
            # DOCS: https://bbs.archlinux.org/viewtopic.php?id=48234
            if (
                "error: failed to init transaction (unable to lock database)\n" in process_stdout_lst
            ):
                if progress_dialog is None:
                    logger.debug("Holding Package")
                    if self.display_package_progress is False:
                        inst_str = [
                            "pacman",
                            "-S",
                            pkg.name,
                            "--needed",
                            "--noconfirm",
                        ]
                        self.pkg_holding_queue.put(
                            (
                                pkg,
                                action,
                                switch,
                                inst_str,
                                progress_dialog,
                            ),
                        )
                else:
                    logger.debug(" ".join(process_stdout_lst))
                    switch.set_sensitive(True)
                    switch.set_state(False)
                    switch.set_active(False)
                    proc = fn.get_pacman_process()
                    message_dialog = MessageDialog(
                        "Warning",
                        "Unable to proceed, pacman lock found!",
                        "Pacman is unable to lock the database inside: %s" % fn.pacman_lockfile,
                        "Pacman is processing: %s" % proc,
                        "warning",
                        False,
                    )
                    message_dialog.show_all()
                    result = message_dialog.run()
                    message_dialog.destroy()
            elif "error: traget not found: %s\n" %pkg.name in process_stdout_lst:
                switch.set_sensitive(True)
                switch.set_state(False)
                switch.set_active(False)
                message_dialog = MessageDialog(
                        "Error",
                        "%s not found!" % pkg.name,
                        "Blackbox unable to process the request!",
                        "Are you sure pacman config is correct?",
                        "error",
                        False,
                    )
                message_dialog.show_all()
                result = message_dialog.run()
                message_dialog.destroy()
            else:
                switch.set_sensitive(True)
                switch.set_state(False)
                switch.set_active(False)
                message_dialog = MessageDialog(
                        "Errors occured",
                        "Errors occured during installation of %s failed" % pkg.name,
                        "Pacman failed to install %s\n" %pkg.name,
                        " ".join(process_stdout_lst),
                        "error",
                        True,
                    )
                message_dialog.show_all()
                result = message_dialog.run()
                message_dialog.destroy()
    if installed is False and action =="uninstall":
        logger.debug("Toggle switch state = False")
        switch.set_sensitive(True)
        switch.set_state(True)
        switch.set_active(True)
        if progress_dialog is not None:
            if progress_dialog.pkg_dialog_closed is False:
                progress_dialog.set_title(
                    "%s uninstalled!" %pkg.name
                )
                progress_dialog.infobar.set_name("infobar_info")
                content =progress_dialog.infobar.get_content_area()
                if content is not None:
                    for widget in content.get_children():
                        content.remove(widget)
                    lbl_install = Gtk.Label(xalign=0, yalign=0)
                    # DOCS: https://stackoverflow.com/questions/40072104/multi-color-text-in-one-gtk-label
                    lbl_install.set_markup(
                        "<b>Package %s installed.</b>" % pkg.name
                    )
                    content.add(lbl_install)
                    if self.timeout_id is not None:
                        # DOCS: https://gtk-rs.org/gtk-rs-core/stable/0.14/docs/glib/source/fn.source_remove.html
                        GLib.source_remove(self.timeout_id)
                        self.timeout_id = None
                    self.timeout_id = GLib.timeout_add(
                        100,
                        reveal_infobar,
                        self,
                        progress_dialog,
                    )
    if installed is True and action == "uninstall":
        # logger.debug("Toggle switch state = False")
        switch.set_sensitive(True)
        switch.set_state(True)
        switch.set_active(True)
        if progress_dialog is not None:
            if progress_dialog.pkg_dialog_closed is False:
                progress_dialog.set_title(
                    "Failed to uninstall %s !" %pkg.name
                )
                progress_dialog.infobar.set_name("infobar_error")
                content =progress_dialog.infobar.get_content_area()
                if content is not None:
                    for widget in content.get_children():
                        content.remove(widget)
                    lbl_install = Gtk.Label(xalign=0, yalign=0)
                    # DOCS: https://stackoverflow.com/questions/40072104/multi-color-text-in-one-gtk-label
                    lbl_install.set_markup(
                        "<b>Package %s uninstallation failed!</b>" % pkg.name
                    )
                    content.add(lbl_install)
                    if self.timeout_id is not None:
                        # DOCS: https://gtk-rs.org/gtk-rs-core/stable/0.14/docs/glib/source/fn.source_remove.html
                        GLib.source_remove(self.timeout_id)
                        self.timeout_id = None
                    self.timeout_id = GLib.timeout_add(
                        100,
                        reveal_infobar,
                        self,
                        progress_dialog,
                    )
        elif progress_dialog is None or progress_dialog.pkg_dialog_closed is True:
            if (
                "error: failed to init transaction (unable to lock database)\n" in process_stdout_lst
            ):
                logger.error(" ".join(process_stdout_lst))
            else:
                message_dialog = MessageDialog(
                    "Errors occured during uninstall",
                    "Errors occured during uninstallation of %s failed" % pkg.name,
                    "Pacman failed to uninstall %s\n" %pkg.name,
                    " ".join(process_stdout_lst),
                    "error",
                    True,
                )
                message_dialog.show_all()
                result = message_dialog.run()
                message_dialog.destroy()


def reveal_infobar(
        self,
        progress_dialog,
):
    progress_dialog.infobar.set_revealed(True)
    progress_dialog.infobar.show_all()
    GLib.source_remove(self.timeout_id)
    self.timeout_id = None

def update_progress_textview(
        self,
        line,
        progress_dialog
):
    if (
        progress_dialog is not None 
        and progress_dialog.pkg_dialog_closed is False 
        and self.in_progress is True
    ):
        buffer = progress_dialog.package_progress_textview.get_buffer()
        # Docs: https://docs.python.org/3/library/asyncio-protocol.html#buffered-streaming-protocols
        if len(line) > 0 or buffer is None:
            buffer.insert(buffer.get_end_iter(), "%s" % line, len("%s" % line))
            text_mark_end = buffer.create_mark("\nend", buffer.get_end_iter(), False)
            # DOCS: https://lazka.github.io/pgi-docs/#Gtk-4.0/classes/TextView.html#Gtk.TextView.scroll_mark_onscreen
            progress_dialog.package_progress_textview.scroll_mark_onscreen(
                text_mark_end
            )
    else:
        line = None
        return False


def check_package_installed(package_name):
    query_str = [
        "pacman",
        "-Qq",
    ]
    try:
        process_pkg_installed = subprocess.run(
            query_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        if package_name in process_pkg_installed.stdout.splitlines():
            return True
        else:
            if check_pacman_localdb(package_name):
                return True
            else:
                return False
    except subprocess.CalledProcessError:
        return False # NOTE : It means package is not installed.

def check_pacman_localdb(package_name):
    query_str = [
        "pacman",
        "-Qi",
        package_name,
    ]
    try:
        process_pkg_installed = subprocess.run(
            query_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,
        )
        if process_pkg_installed.returncode == 0:
            for line in process_pkg_installed.stdout.decode("UTF-8").splitlines():
                if line.startswith("Name        :"):
                    if line.replace(" ", "").split("Name:")[1].strip() == package_name:
                        return True
                if line.startswith("Replaces        :"):
                    replaces = line.split("Replaces        :")[1].strip()
                    if len(replaces) > 0:
                        if package_name in replaces:
                            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False # LOC: 387