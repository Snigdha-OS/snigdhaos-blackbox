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

# Function to print in green (success)
success() {
    echo -e "\033[32m$1\033[0m"
}

# Function to print in red (error)
error() {
    echo -e "\033[31m$1\033[0m"
}

# Function to print in yellow (warning)
warning() {
    echo -e "\033[33m$1\033[0m"
}

# Function to log output to a log file
log() {
    echo "$(date) - $1" >> "$LOGFILE"
}

# Log file location
LOGFILE="/tmp/setup_script.log"

# Clear the previous log
> "$LOGFILE"

# Display help if the user asks for it
if [ "$1" == "--help" ]; then
    usage
fi

# Check if package list file is provided and valid
if [ -z "$2" ] || [ ! -f "$2" ]; then
    error "Package list file is missing or invalid."
    usage
fi

# Check if service script file is provided and valid
if [ -n "$3" ] && [ ! -f "$3" ]; then
    warning "Service script file ($3) not found. Skipping service enabling."
fi

# Step 1: Optional Setup Preparation
if [ -n "$1" ] && [ -e "$1" ]; then
    echo ""
    echo "Preparing Setup..."
    log "Preparing Setup..."
    echo ""
fi

# Step 2: Installing Packages
echo ""
echo "Installing Packages! Please Wait..."
log "Starting package installation..."

# Generate the list of installable packages
installable_packages=$(comm -12 <(pacman -Slq | sort) <(sed 's/\s/\n/g' - <"$2" | sort))

# Check if any valid packages are available
if [ -z "$installable_packages" ]; then
    error "No packages found to install from the provided list."
    log "No valid packages found."
    exit 1
fi

# Attempt to install the packages
echo "Installing the following packages: $installable_packages"
log "Installing packages: $installable_packages"

if ! sudo pacman -S --needed $installable_packages; then
    error "Package installation failed. Please check the package list and try again."
    log "Package installation failed."
    exit 1
else
    # Remove the package list file after successful installation
    rm "$2"
    success "Packages installed successfully."
    log "Packages installed successfully."
fi

# Step 3: Enabling Services (if any)
if [ -n "$3" ] && [ -f "$3" ]; then
    echo ""
    echo "Enabling Services (If Any)..."
    log "Enabling services..."

    # Execute the service script with sudo
    if ! sudo bash - <"$3"; then
        error "Failed to enable services from the script. Please check the script."
        log "Service enabling failed."
        exit 1
    else
        success "Services enabled successfully."
        log "Services enabled successfully."
    fi
fi

# Final prompt
echo ""
read -p "Press Enter to return to Snigdha OS Blackbox." 
