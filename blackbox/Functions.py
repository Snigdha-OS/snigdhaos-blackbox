#!/bin/python

import os
from os import makedirs
import sys
import gi
import subprocess
# import logging
from logging import Logger

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
        Logger.error(e)

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
