#!/bin/bash

######################################################################################################################

sudo pacman -S wget --noconfirm --needed

echo "Getting the Snigdha OS keys from the Snigdha PS repo - report if link is broken"
sudo wget https://github.com/arcolinux/arcolinux_repo/raw/main/x86_64/arcolinux-keyring-20251209-3-any.pkg.tar.zst -O /tmp/arcolinux-keyring-20251209-3-any.pkg.tar.zst
sudo pacman -U --noconfirm --needed /tmp/arcolinux-keyring-20251209-3-any.pkg.tar.zst

echo "Getting the latest arcolinux mirrors file - report if link is broken"
sudo wget https://github.com/arcolinux/arcolinux_repo/raw/main/x86_64/arcolinux-mirrorlist-git-23.06-01-any.pkg.tar.zst -O /tmp/arcolinux-mirrorlist-git-23.06-01-any.pkg.tar.zst
sudo pacman -U --noconfirm --needed /tmp/arcolinux-mirrorlist-git-23.06-01-any.pkg.tar.zst
	
######################################################################################################################

if grep -q snigdhaos-core /etc/pacman.conf; then

	echo "Snigdha OS repos are already in /etc/pacman.conf"

else

echo '
[snigdhaos-core]
SigLevel = PackageRequired DatabaseNever
Include = /etc/pacman.d/snigdhaos-mirrorlist

[snigdhaos-extra]
SigLevel = PackageRequired DatabaseNever
Include = /etc/pacman.d/snigdhaos-mirrorlist' | sudo tee --append /etc/pacman.conf

fi

echo "DONE - UPDATE NOW"