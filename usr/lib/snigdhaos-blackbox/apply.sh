#!/bin/sh

# Function to print usage instructions
usage() {
    echo "Usage: $0 [<file1>] <package_list_file> [<service_script_file>]"
    echo ""
    echo "Arguments:"
    echo "  <file1>                Optional. Any file or directory to check before setup."
    echo "  <package_list_file>    Required. A file containing a list of packages to install."
    echo "  <service_script_file>  Optional. A script to enable services (if any)."
    echo ""
    exit 1
}

# Display help if the user asks for it
if [ "$1" == "--help" ]; then
    usage
fi

# Check if package list file is provided and valid
if [ -z "$2" ] || [ ! -f "$2" ]; then
    echo "Error: Package list file is missing or invalid."
    usage
fi

# Check if service script file is provided and valid
if [ -n "$3" ] && [ ! -f "$3" ]; then
    echo "Warning: Service script file ($3) not found. Skipping service enabling."
fi

# Step 1: Optional Setup Preparation
if [ -n "$1" ] && [ -e "$1" ]; then
    echo ""
    echo "Preparing Setup..."
    echo ""
fi

# Step 2: Installing Packages
echo ""
echo "Installing Packages! Please Wait..."
echo ""

# Generate the list of installable packages
installable_packages=$(comm -12 <(pacman -Slq | sort) <(sed 's/\s/\n/g' - <"$2" | sort))

# Check if any valid packages are available
if [ -z "$installable_packages" ]; then
    echo "No packages found to install from the provided list."
    exit 1
fi

# Attempt to install the packages
echo "Installing the following packages: $installable_packages"
if ! sudo pacman -S --needed $installable_packages; then
    echo "Error: Package installation failed. Please check the package list and try again."
    exit 1
else
    # Remove the package list file after successful installation
    rm "$2"
    echo "Packages installed successfully."
fi

# Step 3: Enabling Services (if any)
if [ -n "$3" ] && [ -f "$3" ]; then
    echo ""
    echo "Enabling Services (If Any)..."
    echo ""
    
    # Execute the service script with sudo
    if ! sudo bash - <"$3"; then
        echo "Error: Failed to enable services from the script. Please check the script."
        exit 1
    else
        echo "Services enabled successfully."
    fi
fi

# Final prompt
echo ""
read -p "Press Enter To Return to Snigdha OS Blackbox."
