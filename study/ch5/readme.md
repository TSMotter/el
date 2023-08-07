# Learning about rootfs


## Referencias
- [The kernel’s command-line parameters](https://www.kernel.org/doc/html/v4.14/admin-guide/kernel-parameters.html)
- [bootz command](https://u-boot.readthedocs.io/en/latest/usage/cmd/bootz.html)

- Talks about users, groups, POSIX file permissions and ownership

- Created a staging directory to be the rootfs
```bash
$ mkdir ~/rootfs
$ cd ~/rootfs
$ mkdir bin dev etc home lib proc sbin sys tmp usr var
$ mkdir usr/bin usr/lib usr/sbin
$ mkdir -p var/log
```

- Getting basic apps through busybox
```bash
$ cd ..
$ source set-path-arm-cortex_a8-linux-gnueabihf
$ git clone git://busybox.net/busybox.git
$ cd busybox
$ git checkout 1_36_1
$ make distclean
$ make defconfig
$ make
$ make CONFIG_PREFIX=/home/ggm/Documents/tsmotter/embedded-linux/rootfs/ install
```

- Getting the basic libs to allow for dynamic linking of busybox (and any other application really, but for now we actually just have busybox)
```bash
# Check the required libs:
$ arm-cortex_a8-linux-gnueabihf-readelf -a bin/busybox | grep "program interpreter"
$ arm-cortex_a8-linux-gnueabihf-readelf -a bin/busybox | grep "Shared library"

# Checking their existence in toolchain's sysroot directory:
$ export SYSROOT=$(arm-cortex_a8-linux-gnueabihf-gcc -print-sysroot)
$ find $SYSROOT -iname "*libc*"
$ find $SYSROOT -iname "*libm*"
$ find $SYSROOT -iname "*libresolv*"

# Copying them into the staging directory
$ cp -a $SYSROOT/lib/ld-linux-armhf.so.3 lib
$ cp -a $SYSROOT/lib/libc.so.6 lib
$ cp -a $SYSROOT/lib/libm.so.6 lib
$ cp -a $SYSROOT/lib/libresolv.so.2 lib
```


- Device nodes
    - Most devices in linux are represented by device nodes
    - Device nodes may be block devices (ex: mass storage devices like SD cards or hard disks)
    - Device nodes may be character devices (ex: pretty much everything else but network interfaces)
    - Creating device nodes
    ```bash
    sudo mknod -m 666 dev/null c 1 3
    sudo mknod -m 600 dev/console c 5 1
    ```

- `proc` and `sys` pseudo filesystems
    - Are pseudo filesystems
    - Represent kernel data as files in a hierarchy of directories
    - Contents on this pseudo filesystem are been formatted on the fly by the kernel
        - Ex: `cat /proc/uptime 1061316.83 690763.21`
    - provide another way to interact with device drivers and other kernel code
    - These pseudo filesystems are mounted in boot time (probably done by the init scripts, which will be covered farther ahead)
    - To creating these pseudo filesystems issue the following commands:
    ```bash
    cd rootfs
    mount -t proc proc /proc
    mount -t sysfs sysfs /sys
    ```


## rootfs into de target

- There are 3 ways in which the rootfs can be transfered to te target so that it can be booted: **initramfs**, **disk image**, **network filesystem**

### initramfs
- aka ramdisk
- filesystem loaded in RAM by the bootloader
- Can be used in fallback maintanenca mode when main fs needs updates
- Can be used as the main fs in small systems
- Contents are volatile (RAM)
- It is in fact a compressed *cpio* archive, which is a unix archive format (like **tar** or **zip** but easier to decode, which requires less kernel code)
- Three ways to create a ramdisk:
    - As a standalone cpio archive
    - As a cpio archive embedded into the kernel image
    - As a device table that the build system handles as part of the build


#### A standalone cpio archive
- Create it and put it into the board
```bash
$ sudo apt install u-boot-tools
$ cd ~/rootfs
$ find . | cpio -H newc -ov --owner root:root > ../initramfs.cpio
$ cd ..
$ gzip initramfs.cpio
$ mkimage -A arm -O linux -T ramdisk -d initramfs.cpio.gz uRamdisk
$ cp uRamdisk /media/ggm/boot/
```

- Boot the board, interrupt u-boot and issue the following:
```bash
Hit any key to stop autoboot:  0 
=> 
=> fatload mmc 0:1 0x80200000 zImage
10387968 bytes read in 668 ms (14.8 MiB/s)
=> fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb
69937 bytes read in 7 ms (9.5 MiB/s)
=> fatload mmc 0:1 0x81000000 uRamdisk
6036531 bytes read in 391 ms (14.7 MiB/s)
=> setenv bootargs console=ttyO0,115200 rdinit=/bin/sh
=> bootz 0x80200000 0x81000000 0x80f00000
## Loading init Ramdisk from Legacy Image at 81000000 ...
   Image Name:   
   Created:      2023-08-01   0:42:04 UTC
   Image Type:   ARM Linux RAMDisk Image (gzip compressed)
   Data Size:    6036467 Bytes = 5.8 MiB
   Load Address: 00000000
   Entry Point:  00000000
   Verifying Checksum ... OK
## Flattened Device Tree blob at 80f00000
   Booting using the fdt blob at 0x80f00000
   Loading Ramdisk to 8fa3e000, end 8ffffbf3 ... OK
   Loading Device Tree to 8fa29000, end 8fa3d130 ... OK

Starting kernel ...
```

- On my first attempt I got an error because of a missing lib
```bash
[    3.726454] Run /bin/sh as init process
/bin/sh: error while loading shared libraries: libresolv.so.2: c[    3.735329] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00007f00
[    3.748531] CPU: 0 PID: 1 Comm: sh Not tainted 6.1.31 #1
[    3.753881] Hardware name: Generic AM33XX (Flattened Device Tree)
[    3.760022]  unwind_backtrace from show_stack+0x10/0x14
[    3.765324]  show_stack from dump_stack_lvl+0x40/0x4c
[    3.770433]  dump_stack_lvl from panic+0x108/0x350
[    3.775283]  panic from make_task_dead+0x0/0x17c
[    3.779975] ---[ end Kernel panic - not syncing: Attempted to kill init! exitcode=0x00007f00 ]---
annot open shared object file: No such file or directory
```

- After fixing the error (adding the missing lib and re-generating the initramfs) the problem was solved and it works:
```bash
[    3.712896] Run /bin/sh as init process
/bin/sh: can't access tty; job control turned off
~ # [    3.754117] mmc0: new high speed SDHC card at address 0007
[    3.761999] mmcblk0: mmc0:0007 SDCIT 7.29 GiB 
[    3.772319]  mmcblk0: p1 p2
[    3.854198] mmc1: new high speed MMC card at address 0001
[    3.861724] mmcblk1: mmc1:0001 MK2704 3.53 GiB 
[    3.871238]  mmcblk1: p1
[    3.877118] mmcblk1boot0: mmc1:0001 MK2704 2.00 MiB 
[    3.886762] mmcblk1boot1: mmc1:0001 MK2704 2.00 MiB 
[    3.895866] mmcblk1rpmb: mmc1:0001 MK2704 512 KiB, chardev (236:0)

~ # ls
bin      etc      lib      proc     sbin     tmp      var
dev      home     linuxrc  root     sys      usr
```

#### A cpio archive embedded into the kernel image
- This option exists for situations where the bootloader does not support loading an initramfs file
- In this case, edit a kernel configuration in `menuconfig` -> `General setup` -> `Initramfs source file(s)` and point to the `cpio` file (not the gzipped one)
- Rebuild the kernel and it should include the initramfs within the kernel
- The commands send to the bootloader should be adapted (there'll be no fatload command pointing to the initramfs file)

#### A device table that the build system handles as part of the build
- A device table is a text file that lists the files, directories, device nodes (ie: `/dev/null`, `/dev/console`), and links that go into an archive or filesystem image.
    - The overwhelming advantage is that it allows you to create entries in the archive file that are owned by the root user, or any other UID, without having root privileges yourself.
- There is a script on linux kernel source code that generates a device table based on a directory
    - For example, to create the initramfs device table for the rootfs directory, and to change the ownership of all files owned by user ID 1000 and group ID 1000 to user and group ID 0, you would use this command:
    - **I did not find this script on my kernel source code!!**
    - **I copied from [this website](https://elixir.bootlin.com/linux/v4.9/source/scripts/gen_initramfs_list.sh) and created it locally**
    ```bash
    bash linux-6.1.31/scripts/gen_initramfs_list.sh -u 1000 -g 1000 rootfs > initramfs-device-table
    ```
    - This command created a device table representing the rootfs directory. The file created can be found versioned here

- Checking the UID and GID of my user on my host machine (it is 1000)
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/rootfs$ cat /etc/group | grep ggm:
ggm:x:1000:
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/rootfs$ cat /etc/passwd | grep ggm
ggm:x:1000:1000:ggm,,,:/home/ggm:/bin/bash
```


## The init program
- The most basic option for an init program is BusyBox's `init` program
    - It starts by reading the `/etc/inittab` file
    - BusyBox init provides a default inittab if none is present in the root filesystem
```bash
$ touch etc/inittab
$ echo "::sysinit:/etc/init.d/rcS
::askfirst:-/bin/ash" >> etc/inittab
$
$ mkdir etc/init.d
$ touch etc/init.d/rcS
$ echo "#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys" >> etc/init.d/rcS
$
$ chmod +x etc/init.d/rcS 
```

- Booting with init program
```bash
Hit any key to stop autoboot:  0 
=> 
=> 
=> fatload mmc 0:1 0x80200000 zImage
10387968 bytes read in 667 ms (14.9 MiB/s)
=> fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb
69937 bytes read in 7 ms (9.5 MiB/s)
=> fatload mmc 0:1 0x81000000 uRamdisk
6148337 bytes read in 397 ms (14.8 MiB/s)
=> setenv bootargs console=ttyO0,115200 rdinit=/sbin/init
=> bootz 0x80200000 0x81000000 0x80f00000
## Loading init Ramdisk from Legacy Image at 81000000 ...
   Image Name:   
   Created:      2023-08-01  23:09:20 UTC
   Image Type:   ARM Linux RAMDisk Image (gzip compressed)
   Data Size:    6148273 Bytes = 5.9 MiB
   Load Address: 00000000
   Entry Point:  00000000
   Verifying Checksum ... OK
## Flattened Device Tree blob at 80f00000
   Booting using the fdt blob at 0x80f00000
   Loading Ramdisk to 8fa22000, end 8ffff0b1 ... OK
   Loading Device Tree to 8fa0d000, end 8fa21130 ... OK

Starting kernel ...
.
.
.
Please press Enter to activate this console. [    3.755869] mmc0: new high speed SDHC card at address 0007
[    3.762359] mmcblk0: mmc0:0007 SDCIT 7.29 GiB 
[    3.770136]  mmcblk0: p1 p2
[    3.863856] mmc1: new high speed MMC card at address 0001
[    3.871397] mmcblk1: mmc1:0001 MK2704 3.53 GiB 
[    3.881960]  mmcblk1: p1
[    3.887218] mmcblk1boot0: mmc1:0001 MK2704 2.00 MiB 
[    3.896898] mmcblk1boot1: mmc1:0001 MK2704 2.00 MiB 
[    3.905964] mmcblk1rpmb: mmc1:0001 MK2704 512 KiB, chardev (236:0)

~ # ps
PID   USER     TIME  COMMAND
    1 0         0:00 init
    2 0         0:00 [kthreadd]
    3 0         0:00 [rcu_gp]

```

- Incrementing inittab to start up the `syslogd` daemon can be done by adding the following line:
```bash
::respawn:/sbin/syslogd -n
```

## User accounts
- Using accounts other then root to execute programs that do not need root privilege protects the system from being completely vulnerable if only one program is vulnerable
- User accounts are configured in /etc/passwd
```bash
$ cd rootfs
$ cat etc/passwd
root:x:0:0:root:/root:/bin/sh
daemon:x:1:1:daemon:/usr/sbin:/bin/false
```

- passwords are actually stored in /etc/shadow which is only accesible by root
```bash
$ cat etc/shadow
root::10933:0:99999:7:::
daemon:*:10933:0:99999:7:::
```

- groups are also relevant in the same way
```bash
$ cat etc/group
root:x:0:
daemon:x:1:
```

- Adding users and groups to the rfs:
```bash
$ touch etc/passwd
$ touch etc/shadow
$ touch etc/group
$ chmod 0600 etc/shadow 
$ cat etc/inittab 
::sysinit:/etc/init.d/rcS
::respawn:/sbin/syslogd -n
::respawn:/sbin/getty 115200 console
```

- Re-generate the ramdisk and re-boot it
- Note that I'm no longer in `/` after logging in, rather I'm in `/root`
```bash
fatload mmc 0:1 0x80200000 zImage; fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb; fatload mmc 0:1 0x81000000 uRamdisk; setenv bootargs console=ttyO0,115200 rdinit=/sbin/init; bootz 0x80200000 0x81000000 0x80f00000
.
.
.
(none) login: 0
Password: 

Login incorrect
(none) login: root
~ #
~ # pwd
/root
~ # ls /
bin      etc      lib      proc     sbin     tmp      var
dev      home     linuxrc  root     sys      usr
```

## Managing device nodes
- The book shows options for handling devices nodes statically and dinamically
- Options are `devtmpfs`, `mdev`, `udev`
- To incorporate `mdev` to the rootfs:
```bash
$ cat etc/init.d/rcS 
#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
echo /sbin/mdev > /proc/sys/kernel/hotplug
mdev -s
$ touch etc/mdev.conf
$ cat etc/mdev.conf
null root:root 666
random root:root 444
urandom root:root 444
```
- re-generate it
```bash
cd ~/Documents/tsmotter/embedded-linux/rootfs/ && find . | cpio -H newc -o --owner root:root > ../initramfs.cpio && cd .. && gzip -f initramfs.cpio && mkimage -A arm -O linux -T ramdisk -d initramfs.cpio.gz uRamdisk && cp uRamdisk /media/ggm/boot/ && md5sum uRamdisk && md5sum /media/ggm/boot/uRamdisk
```

- boot it
```bash
fatload mmc 0:1 0x80200000 zImage; fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb; fatload mmc 0:1 0x81000000 uRamdisk; setenv bootargs console=ttyO0,115200 rdinit=/sbin/init; bootz 0x80200000 0x81000000 0x80f00000
.
.
.
(none) login: root
~ # 
~ # ls /dev
autofs           ptyrf            tty20            ttyq9
console          ptys0            tty21            ttyqa
cpu_dma_latency  ptys1            tty22            ttyqb
full             ptys2            tty23            ttyqc
gpiochip0        ptys3            tty24            ttyqd
gpiochip1        ptys4            tty25            ttyqe
gpiochip2        ptys5            tty26            ttyqf
gpiochip3        ptys6            tty27            ttyr0
hwrng            ptys7            tty28            ttyr1
.
.
.
ptyra            tty16            ttyq4            vcsa1
ptyrb            tty17            ttyq5            vcsu
ptyrc            tty18            ttyq6            vcsu1
ptyrd            tty19            ttyq7            vga_arbiter
ptyre            tty2             ttyq8            zero
~ # 
```


- After setting up device nodes, it is time to set up the networking

## Configuring the network

```bash
$ mkdir etc/network
$ touch etc/network/interfaces
$ touch etc/network/if-pre-up.d
$ touch etc/network/if-up.d
$ touch var/run
$ cat etc/network/interfaces 
auto lo
iface lo inet loopback
auto eth0
iface eth0 inet static
address 192.168.1.101
netmask 255.255.255.0

# name service switch (NSS) is used by glibc to control the way that names are resolved to numbers for networking and users
$ touch etc/nsswitch.conf
$ cat etc/nsswitch.conf 
passwd: files
group: files
shadow: files
hosts: files dns
networks: files
protocols: files
services: files

# Copy from host machine
$ cp /etc/networks etc
$ cp /etc/protocols etc
$ cp /etc/services etc

# loopback address
$ cat etc/hosts 
127.0.0.1 localhost

# Copy the libraries that perform name resolution 
$ cp -a $SYSROOT/lib/libnss* lib
```
- Could generate another ramdisk file and test it but will skip directly to mounting the rootfs

## Creating filesystem images with device tables

- kernel command line documentation:
    - https://www.kernel.org/doc/html/v4.14/admin-guide/kernel-parameters.html

- Install the `genext2fs` tool
    - This tool creates an ext2 filesystem image from directories/files as normal (non-root) user
```bash
sudo apt install genext2fs
```
- Create the example device table file
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ cat device-table.txt 
/dev d 755 0 0 - - - - -
/dev/null c 666 0 0 1 3 0 0 -
/dev/console c 600 0 0 5 1 0 0 -
/dev/ttyO0 c 600 0 0 252 0 0 0 -
```

- Generate the fs
- **This command failed in my case:**
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ genext2fs -b 4096 -d rootfs -D device-table.txt -U rootfs.ext2
copying from directory rootfs
genext2fs: couldn't allocate a block (no free space)
```
- Looks like it is because my rootfs is ~16MB, which of couse is > 4MB (-b 4096)
- The following worked:
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ genext2fs -b 16384 -d rootfs -D device-table.txt -U rootfs.ext2
copying from directory rootfs
nodes fixup and creation from device table device-table.txt
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ du -h --max-depth=1 rootfs | sort -h
4,0K    rootfs/dev
4,0K    rootfs/home
4,0K    rootfs/proc
4,0K    rootfs/sbin
4,0K    rootfs/sys
4,0K    rootfs/tmp
8,0K    rootfs/var
12K    rootfs/usr
72K    rootfs/etc
1,1M    rootfs/bin
15M    rootfs/lib
16M    rootfs
```

- Plug in SD card into host machine and `dd` the generated filesystem to the rootfs partition of the sd card
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ sudo dd if=rootfs.ext2 of=/dev/mmcblk0p2
[sudo] password for ggm: 
32768+0 records in
32768+0 records out
16777216 bytes (17 MB, 16 MiB) copied, 1,80198 s, 9,3 MB/s
```

- Boot it - **NOT WORKING**
```bash
fatload mmc 0:1 0x80200000 zImage
fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb
setenv bootargs console=ttyO0,115200 root=/dev/mmcblk0p2
bootz 0x80200000 - 0x80f00000
```
- Managed to make it work with the following addaptions:
```bash
fatload mmc 0:1 0x80200000 zImage
fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb
setenv bootargs console=ttyO0,115200 root=/dev/mmcblk0p2 rootdelay=2 rootfstype=ext2
bootz 0x80200000 - 0x80f00000
.
.
.
[    3.363460] mmc1: SDHCI controller on 481d8000.mmc [481d8000.mmc] using External DMA
[    3.372924] mmc0: SDHCI controller on 48060000.mmc [48060000.mmc] using External DMA
[    3.418675] mmc0: new high speed SDHC card at address 0007
[    3.426756] mmcblk0: mmc0:0007 SDCIT 7.29 GiB 
[    3.436535]  mmcblk0: p1 p2
[    3.444422] mmc1: new high speed MMC card at address 0001
[    3.452486] mmcblk1: mmc1:0001 MK2704 3.53 GiB 
[    3.462491]  mmcblk1: p1
[    3.467869] mmcblk1boot0: mmc1:0001 MK2704 2.00 MiB 
[    3.477590] mmcblk1boot1: mmc1:0001 MK2704 2.00 MiB 
[    3.485312] mmcblk1rpmb: mmc1:0001 MK2704 512 KiB, chardev (236:0)
[    5.317192] EXT4-fs (mmcblk0p2): mounting ext2 file system using the ext4 subsystem
[    5.331422] EXT4-fs (mmcblk0p2): mounted filesystem without journal. Quota mode: disabled.
[    5.339968] VFS: Mounted root (ext2 filesystem) readonly on device 179:2.
[    5.349790] devtmpfs: mounted
[    5.355844] Freeing unused kernel image (initmem) memory: 2048K
[    5.362594] Run /sbin/init as init process
mount: mounting devtmpfs on /dev failed: Device or resource busy
/etc/init.d/rcS: line 5: can't create /proc/sys/kernel/hotplug: nonexistent directory
Jan  1 00:00:06 (none) syslog.info syslogd started: BusyBox v1.36.1

(none) login: root
login: can't change directory to '/root': No such file or directory
Jan  1 00:00:10 (none) auth.info login[79]: root login on 'console'
/ # 
```



## Mounting the rootfs using NFS
- Configure NFS server on the host machine 
```bash
sudo apt install nfs-kernel-server
```

- Configure the directories to be exposed and restart nfs
```bash
$ echo "/home/ggm/Documents/tsmotter/embedded-linux/rootfs *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
$ systemctl restart nfs-server.service
```

- Rebuild the kernel with the `CONFIG_ROOT_NFS` option enabled if it isn't already
    - In my case it seems to be already enabled
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/linux-6.1.31$ cat .config | grep ROOT_NFS
CONFIG_ROOT_NFS=y
```

- Add the uEnv.txt file to the boot partition of the sd card so that uboot knows the boot commands / kernel command line
```bash
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ cat el/study/ch5/uEnv.txt 
serverip=192.168.1.1
ipaddr=192.168.1.101
npath=/home/ggm/Documents/tsmotter/embedded-linux/rootfs
bootargs=console=ttyO0,115200 root=/dev/nfs rw nfsroot=${serverip}:${npath},v3 ip=${ipaddr}
uenvcmd=fatload mmc 0:1 80200000 zImage;fatload mmc 0:1 80f00000 am335x-boneblack.dtb;bootz 80200000 - 80f00000
```


- Boot it on the bbb

- **The outcome is was NOT the expected**:
    - Was not able to properly load the filesystem
```bash
.
.
.
[    3.576087] mmcblk1rpmb: mmc1:0001 MK2704 512 KiB, chardev (236:0)
[    6.644247] cpsw-switch 4a100000.switch eth0: Link is Up - 100Mbps/Full - flow control off
[    6.652758] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[    6.683328] Sending DHCP and RARP requests ...... timed out!
[   80.850891] cpsw-switch 4a100000.switch eth0: Link is Down
[   80.861424] IP-Config: Retrying forever (NFS root)...
[   80.866805] cpsw-switch 4a100000.switch: starting ndev. mode: dual_mac
[   80.954655] SMSC LAN8710/LAN8720 4a101000.mdio:00: attached PHY driver (mii_bus:phy_addr=4a101000.mdio:00, irq=POLL)
[   84.084237] cpsw-switch 4a100000.switch eth0: Link is Up - 100Mbps/Full - flow control off
[   84.092736] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[   84.123318] Sending DHCP and RARP requests ...... timed out!
[  156.630870] cpsw-switch 4a100000.switch eth0: Link is Down
[  156.641319] IP-Config: Retrying forever (NFS root)...
[  156.646690] cpsw-switch 4a100000.switch: starting ndev. mode: dual_mac
[  156.734655] SMSC LAN8710/LAN8720 4a101000.mdio:00: attached PHY driver (mii_bus:phy_addr=4a101000.mdio:00, irq=POLL)
[  162.004298] cpsw-switch 4a100000.switch eth0: Link is Up - 100Mbps/Full - flow control off
[  162.012794] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[  162.053314] Sending DHCP and RARP requests ...... timed out!
[  252.060868] cpsw-switch 4a100000.switch eth0: Link is Down
[  252.071192] IP-Config: Retrying forever (NFS root)...
[  252.076547] cpsw-switch 4a100000.switch: starting ndev. mode: dual_mac
[  252.164774] SMSC LAN8710/LAN8720 4a101000.mdio:00: attached PHY driver (mii_bus:phy_addr=4a101000.mdio:00, irq=POLL)
[  255.284221] cpsw-switch 4a100000.switch eth0: Link is Up - 100Mbps/Full - flow control off
[  255.292715] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
.
.
.
```

- Possibly problem on the hostmachine network configuration
```
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ sudo lshw -class network
  *-network                 
       description: Wireless interface
       product: Cannon Lake PCH CNVi WiFi
       vendor: Intel Corporation
       physical id: 14.3
       bus info: pci@0000:00:14.3
       logical name: wlp0s20f3
       version: 10
       serial: 5c:87:9c:96:63:ba
       width: 64 bits
       clock: 33MHz
       capabilities: pm msi pciexpress msix bus_master cap_list ethernet physical wireless
       configuration: broadcast=yes driver=iwlwifi driverversion=5.19.0-50-generic firmware=46.fae53a8b.0 9000-pu-b0-jf-b0- ip=192.168.0.13 latency=0 link=yes multicast=yes wireless=IEEE 802.11
       resources: irq:16 memory:a4398000-a439bfff
  *-network
       description: Ethernet interface
       product: RTL8111/8168/8411 PCI Express Gigabit Ethernet Controller
       vendor: Realtek Semiconductor Co., Ltd.
       physical id: 0.1
       bus info: pci@0000:06:00.1
       logical name: enp6s0f1
       version: 12
       serial: 08:97:98:65:5b:df
       size: 100Mbit/s
       capacity: 1Gbit/s
       width: 64 bits
       clock: 33MHz
       capabilities: pm msi pciexpress msix vpd bus_master cap_list ethernet physical tp mii 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
       configuration: autonegotiation=on broadcast=yes driver=r8169 driverversion=5.19.0-50-generic duplex=full firmware=rtl8411-2_0.0.1 07/08/13 latency=0 link=yes multicast=yes port=twisted pair speed=100Mbit/s
       resources: irq:17 ioport:3000(size=256) memory:a4204000-a4204fff memory:a4200000-a4203fff
ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux$ sudo ethtool enp6s0f1
Settings for enp6s0f1:
    Supported ports: [ TP     MII ]
    Supported link modes:   10baseT/Half 10baseT/Full
                            100baseT/Half 100baseT/Full
                            1000baseT/Full
    Supported pause frame use: Symmetric Receive-only
    Supports auto-negotiation: Yes
    Supported FEC modes: Not reported
    Advertised link modes:  10baseT/Half 10baseT/Full
                            100baseT/Half 100baseT/Full
                            1000baseT/Full
    Advertised pause frame use: Symmetric Receive-only
    Advertised auto-negotiation: Yes
    Advertised FEC modes: Not reported
    Link partner advertised link modes:  10baseT/Half 10baseT/Full
                                         100baseT/Half 100baseT/Full
    Link partner advertised pause frame use: No
    Link partner advertised auto-negotiation: Yes
    Link partner advertised FEC modes: Not reported
    Speed: 100Mb/s
    Duplex: Full
    Auto-negotiation: on
    master-slave cfg: preferred slave
    master-slave status: slave
    Port: Twisted Pair
    PHYAD: 0
    Transceiver: external
    MDI-X: Unknown
    Supports Wake-on: pumbg
    Wake-on: d
    Link detected: yes

```