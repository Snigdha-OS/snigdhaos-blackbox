#!/bin/bash

# Install 'Wget' via pacman
sudo pacman -S wget --noconfirm --needed

URL_KEYRING=""
PACKAGE_FILE="" 
echo
echo "Downloading Snigdha OS Keyring..."
echo

sudo wget "$URL_KEYRING" -O /tmp/$PACKAGE_FILE

# Installing File Locally
sudo pacman -U --noconfirm --needed /tmp/$PACKAGE_FILE

if grep -q snigdhaos- /etc/pacman.conf; then
    echo
    echo "Snigdha OS Repository/Mirrorlist already installed!"
    echo
else
    echo '
    [snigdhaos-core]
    SigLevel = Never
    Include = /etc/pacman.d/snigdhaos-mirrorlist

    [snigdhaos-extra]
    SigLevel = Never
    Include = /etc/pacman.d/snigdhaos-mirrorlist' | 
    sudo tee --append /etc/pacman.conf
fi

echo
echo "Finished! Now Synchronize DB..."
echo
