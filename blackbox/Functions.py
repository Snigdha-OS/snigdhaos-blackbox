#!/bin/python

import os
import gi

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
