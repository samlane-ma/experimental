#!/usr/bin/env bash

IMAGE="ubuntu-20.10-preinstalled-desktop-arm64+raspi.img"
MOUNT="/mnt/pi"
NAMESERVER=1.1.1.1

if [ "$(id -u)" -ne 0 ]; then
  echo "You need to be root to run this."
  exit 1
fi

if [ ! -f "/usr/bin/qemu-arm-static" ]; then
  echo "Please make sure to install the following packages:"
  echo "   binfmt-support"
  echo "   qemu"
  echo "   qemu-user-static"
  exit 1
fi

CURRENT_DIR=$(pwd)
sudo -u $SUDO_USER wget https://cdimage.ubuntu.com/releases/20.10/release/$IMAGE.xz
sudo -u $SUDO_USER xz -d -v $IMAGE.xz
OFFSET=$(parted ubuntu-20.10-preinstalled-desktop-arm64+raspi.img unit b print | grep "ext4" | awk '{ print substr($2,0,length($2)-1) }')
mkdir -p $MOUNT
mount -o loop,offset=$OFFSET $IMAGE $MOUNT
cp /usr/bin/qemu-arm-static $MOUNT/usr/bin/
cp setup-budgie.dontrun $MOUNT/usr/bin/setup-budgie.sh
chmod +x $MOUNT/usr/bin/setup-budgie.sh
rm $MOUNT/run/systemd/resolve/stub-resolv.conf
echo "nameserver $NAMESERVER" > tempconf.tmp
cp tempconf.tmp $MOUNT/run/systemd/resolve/stub-resolv.conf
rm tempconf.tmp
cd $MOUNT
mount -t proc /proc proc/
mount --rbind /sys sys/
mount --rbind /dev dev/

chroot $MOUNT /usr/bin/setup-budgie.sh
rm $MOUNT/usr/bin/qemu-arm-static
cd $CURRENT_DIR
# Next line commented because it takes a long time to recompress
# sudo -u $SUDO_USER xz -v $IMAGE

