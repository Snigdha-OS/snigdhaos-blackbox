#!/bin/python

import os
from os import makedirs
import sys
import gi
import subprocess
import logging
import datetime
from datetime import datetime
from datetime import timedelta
# from logging import Logger
import shutil
import Settings
from logging.handlers import TimedRotatingFileHandler

from ui.GUI import *

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

    except Exception as e:
        print(e)