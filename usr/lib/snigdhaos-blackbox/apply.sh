#!/bin/sh

if [ -e "$1" ]; then
    echo ""
    echo "Preparing Setup..."
    echo ""
fi

echo ""
echo "Installing Packages! Please Wait..."
echo ""

installable_packages=$(comm -12 <(pacman -Slq | sort) <(sed s/\\s/\\n/g - <$2 | sort))
sudo pacman -S --needed $installable_packages && rm $2 || { read -p "Error Occured! Press Enter to Return To Snigdha OS BlackBox"; exit; }

if [ -e "$3" ]; then
    echo ""
    echo "Enabling Services(If Any)"
    echo ""
    sudo bash - <$3
fi

echo ""
read -p "Press Enter To Return to Snigdha OS Blackbox."