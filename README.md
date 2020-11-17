# experimental

## budgie-image

This requires the following:
- binfmt-support
- qemu
- qemu-user-static

This script will:

- Download the Ubuntu Raspberry Pi Preinstalled Desktop image
- Extract the image
- Determine the correct offset and mount the image
- Set up the required bind mounts
- Add a nameserver to the image file's resolv.conf
- Copy the setup script to the mounted image
- Run the setup script on the mounted image using chroot
- Remove files added temporarily
- Compress the image back to .xz

The script executed on the Pi image via chroot will:
- download the ubuntu-budgie-welcome snap and move the files to the snap seed directory
- modify the snap seed.yaml / modify snapd.seeded.service / erase state.json
- (these modifications will trigger the snaps to re-seed on first reboot after install)
- remove gnome-shell and gdm3
- remove other packages not part of Ubuntu Budgie
- install Ubuntu Budgie
- install the Ubuntu Budgie setup slideshow
- reset the resolv.conf changes

Packages added:
- ubuntu-budgie-desktop
- oem-config-slideshow-ubuntu-budgie

Packages removed:
- network-manager-config-connectivity-ubuntu
- gnome-initial-setup
- ubuntu-report
- eog
- gnome-terminal 
- nautilus 
- xdg-desktop-portal-gtk
- apt-config-icons-hidpi
- gamemode seahorse
- yaru-theme-gnome-shell
- yaru-theme-gtk
- yaru-theme-icon
- yaru-theme-sound
- ubuntu-wallpapers
- gnome-session-canberra
- ubuntu-settings
- gsettings-ubuntu-schemas
- xcursor-themes
- realmd
- adcli
- gnome-getting-started-docs
- shotwell
