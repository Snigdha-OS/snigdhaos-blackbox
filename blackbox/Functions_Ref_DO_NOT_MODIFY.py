import os
import sys
import shutil
import psutil
import datetime

# import time
import subprocess
import threading  # noqa
import gi

# import configparser
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa


log_dir = "/var/log/snigdhaos/"
aai_log_dir = "/var/log/snigdhaos/aai/"

def create_log(self):
    print("Making log in /var/log/snigdhaos")
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d-%H-%M-%S")
    destination = aai_log_dir + "aai-log-" + time
    command = "sudo pacman -Q > " + destination
    subprocess.call(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
    )

def _get_position(lists, value):
    data = [string for string in lists if value in string]
    position = lists.index(data[0])
    return position

def permissions(dst):
    try:
        groups = subprocess.run(
            [
                "sh", 
                "-c", 
                "id " + sudo_username
            ],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for x in groups.stdout.decode().split(" "):
            if "gid" in x:
                g = x.split("(")[1]
                group = g.replace(")", "").strip()
        subprocess.call(
            [
                "chown", 
                "-R", 
                sudo_username + ":" + group, 
                dst
            ], 
            shell=False,
        )
    except Exception as e:
        print(e)

sudo_username = os.getlogin()
home = "/home/" + str(sudo_username)

sddm_default = "/etc/sddm.conf"
sddm_default_original = "/usr/local/share/snigdhaos/sddm/sddm.conf"

sddm_default_d1 = "/etc/sddm.conf"
sddm_default_d2 = "/etc/sddm.conf.d/kde_settings.conf"
sddm_default_d2_dir = "/etc/sddm.conf.d/"
sddm_default_d_sddm_original_1 = "/usr/local/share/snigdhaos/sddm.conf.d/sddm.conf"
sddm_default_d_sddm_original_2 = (
    "/usr/local/share/snigdhaos/sddm.conf.d/kde_settings.conf"
)

if os.path.exists("/etc/sddm.conf.d/kde_settings.conf"):
    sddm_conf = "/etc/sddm.conf.d/kde_settings.conf"
else:
    sddm_conf = "/etc/sddm.conf"

snigdhaos_mirrorlist = "/etc/pacman.d/snigdhaos-mirrorlist"
snigdhaos_mirrorlist_original = "/usr/local/share/snigdhaos/snigdhaos-mirrorlist"
pacman = "/etc/pacman.conf"
neofetch_config = home + "/.config/neofetch/config.conf"
autostart = home + "/.config/autostart/"

srepo = "[snigdhaos-core]\n\
SigLevel = Required DatabaseOptional\n\
Include = /etc/pacman.d/snigdhaos-mirrorlist"

serepo = "[snigdhaos-extra]\n\
SigLevel = Required DatabaseOptional\n\
Include = /etc/pacman.d/snigdhaos-mirrorlist"

def show_in_app_notification(self, message):
    if self.timeout_id is not None:
        GLib.source_remove(self.timeout_id)
        self.timeout_id = None
    self.notification_label.set_markup(
        '<span foreground="white">' + message + "</span>"
    )
    self.notification_revealer.set_reveal_child(True)
    self.timeout_id = GLib.timeout_add(3000, timeOut, self)

def timeOut(self):
    close_in_app_notification(self)

def close_in_app_notification(self):
    self.notification_revealer.set_reveal_child(False)
    GLib.source_remove(self.timeout_id)
    self.timeout_id = None

def test(dst):
    for root, dirs, filesr in os.walk(dst):
        # print(root)
        for folder in dirs:
            pass
            # print(dst + "/" + folder)
            for file in filesr:
                pass
                # print(dst + "/" + folder + "/" + file)
        for file in filesr:
            pass

def copy_func(src, dst, isdir=False):
    if isdir:
        subprocess.run(["cp", "-Rp", src, dst], shell=False)
    else:
        subprocess.run(["cp", "-p", src, dst], shell=False)

def source_shell(self):
    process = subprocess.run(["sh", "-c", 'echo "$SHELL"'], stdout=subprocess.PIPE)

    output = process.stdout.decode().strip()
    print(output)
    if output == "/bin/bash":
        subprocess.run(
            [
                "bash",
                "-c",
                "su - " + sudo_username + ' -c "source ' + home + '/.bashrc"',
            ],
            stdout=subprocess.PIPE,
        )
    elif output == "/bin/zsh":
        subprocess.run(
            ["zsh", "-c", "su - " + sudo_username + ' -c "source ' + home + '/.zshrc"'],
            stdout=subprocess.PIPE,
        )

def run_as_user(script):
    subprocess.call(["su - " + sudo_username + " -c " + script], shell=False)

def MessageBox(self, title, message):
    md2 = Gtk.MessageDialog(
        parent=self,
        flags=0,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text=title,
    )
    md2.format_secondary_markup(message)
    md2.run()
    md2.destroy()

def rgb_to_hex(rgb):
    if "rgb" in rgb:
        rgb = rgb.replace("rgb(", "").replace(")", "")
        vals = rgb.split(",")
        return "#{0:02x}{1:02x}{2:02x}".format(
            clamp(int(vals[0])), clamp(int(vals[1])), clamp(int(vals[2]))
        )
    return rgb

def clamp(x):
    return max(0, min(x, 255))

def _get_variable(lists, value):
    data = [string for string in lists if value in string]
    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]
        for i in data1:
            if i[:4].find("#") != -1:
                data.remove(i)
    if data:
        data_clean = [data[0].strip("\n").replace(" ", "")][0].split("=")
    return data_clean

def check_value(list, value):
    data = [string for string in list if value in string]
    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]
        for i in data1:
            if i[:4].find("#") != -1:
                data.remove(i)
    return data

def check_backups(now):
    if not os.path.exists(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H")):
        os.makedirs(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H"), 0o777)
        permissions(home + "/" + bd + "/Backup-" + now.strftime("%Y-%m-%d %H"))

def file_check(file):
    if os.path.isfile(file):
        return True
    return False

def path_check(path):
    if os.path.isdir(path):
        return True
    return False

def gtk_check_value(my_list, value):
    data = [string for string in my_list if value in string]
    if len(data) >= 1:
        data1 = [string for string in data if "#" in string]
        for i in data1:
            if i[:4].find("#") != -1:
                data.remove(i)
    return data

def gtk_get_position(my_list, value):
    data = [string for string in my_list if value in string]
    position = my_list.index(data[0])
    return position

def get_shortcuts(conflist):
    sortcuts = _get_variable(conflist, "shortcuts")
    shortcuts_index = _get_position(conflist, sortcuts[0])
    return int(shortcuts_index)

def get_commands(conflist):
    commands = _get_variable(conflist, "commands")
    commands_index = _get_position(conflist, commands[0])
    return int(commands_index)

def check_lightdm_value(list, value):
    data = [string for string in list if value in string]
    return data

def check_sddm_value(list, value):
    data = [string for string in list if value in string]
    return data

def hblock_get_state(self):
    lines = int(
        subprocess.check_output("wc -l /etc/hosts", shell=True).strip().split()[0]
    )
    if os.path.exists("/usr/local/bin/hblock") and lines > 100:
        return True
    self.firstrun = False
    return False

def do_pulse(data, prog):
    prog.pulse()
    return True

def copytree(self, src, dst, symlinks=False, ignore=None):  # noqa
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(e)
                os.unlink(d)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except Exception as e:
                print(e)
                print("ERROR2")
                self.ecode = 1
        else:
            try:
                shutil.copy2(s, d)
            except:  # noqa
                print("ERROR3")
                self.ecode = 1

def checkIfProcessRunning(processName):
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name", "create_time"])
            if processName == pinfo["pid"]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)