# 6: Selecting a Build System

## References
- A build system should be able to:

    - Build the following from upstream source code:

        - Toolchain

        - Bootloader

        - Kernel

        - Root filesystem

- Build system should be able to:

    - Download source code from upstream (git, archive, etc)

    - Apply patches, local configurations, etc

    - Build all the components

    - Create staging area and assemble the root filesystem

    - Output image files in various formats, ready to be loaded onto the target

- A great build system will also:

    - Add your own packages containing apps / kernel changes / etc

    - Be versatile to allow selecting amongst different filesystem profiles (large, small, minimal, etc)

    - Create an standalone SDK that can be distributed to other developers without the need to install a full build system

    - Help managing the licenses for each of the elements that compose the system

- Most traditional options are *buildroot* and *yocto*

- Mainstream Linux distros are constructed from a collection of binary packages in either RPM or DEB format

    - RPM (Red Hat Package Manager)

    - DEB (Debian)

        - IPK (Itsy Package) - lightweight format common in embedded devices which is based on DEB

- Having a package manager running on the target allows for an easy path to deploy new packages to it in run time without the need to reflash a complete image

## Buildroot

- Primary aim of Buildroot is building rootfilesystem images (although it can also build bootloader, kernel and toolchain)

- Uses GNU Make as the main build tool

```bash
ggm@gAN515-52:~/embedded-linux/ch6/ $ git clone git://git.buildroot.net/buildroot -b 2023.02.9
ggm@gAN515-52:~/embedded-linux/ch6/ $ cd buildroot/
ggm@gAN515-52:~/embedded-linux/ch6/buildroot/ ((HEAD detached at 2023.02.9))$ git log -n1 --oneline --decorate
df57de12f9 (HEAD, tag: 2023.02.9) Update for 2023.02.9
ggm@gAN515-52:~/embedded-linux/ch6/buildroot/ ((HEAD detached at 2023.02.9))$ make raspberrypi0w_defconfig
ggm@gAN515-52:~/embedded-linux/ch6/buildroot/ ((HEAD detached at 2023.02.9))$ make
```

- Buildroot uses the Kconfig / Kbuild mechanism for configuration / build

    - This means that the whole configuration of the system can be done via graphical menu, using `make` on the target `menuconfig`, like so: `make menuconfig`

- Also, there is over 100 configurations to use as basis for your project in `configs/`

    - These can also be listed by using `make` on the target `list-defconfigs`, like so: `make list-defconfigs`

- Outputs:

    - `dl/`: This contains archives of the upstream projects that Buildroot has built.

    - `output/`: This contains all the intermediate and final compiled resources.

    - `output/build/`: Here, you will find the build directory for each component.

    - `output/host/`: This contains various tools required by Buildroot that run on the host, including the executables of the toolchain (in output/host/usr/bin).
    
    - `output/images/`: This is the most important of all since it contains the results of the build. Depending on what you selected when configuring, you will find a bootloader, a kernel, and one or more root filesystem images.
    
    - `output/staging/`: This is a symbolic link to sysroot of the toolchain.

    - `output/target/`: This is the staging area for the root directory. Note that you cannot use it as a root filesystem as it stands because the file ownership and the permissions are not set correctly. Buildroot uses a device table, as described in the previous chapter, to set ownership and permissions when the filesystem image is created in the image/ directory.

- These files are useful for generating a bootable ".img" file present in `output/images/`
```bash
ggm@gAN515-52:~/embedded-linux/ch6/buildroot ((no branch))$ ll board/raspberrypi0w/ | grep post-build
-rwxrwxr-x  1 ggm ggm  659 fev 26 20:44 post-build.sh*
ggm@gAN515-52:~/embedded-linux/ch6/buildroot ((no branch))$ ll board/raspberrypi0w/ | grep raspberrypi0w
-rw-rw-r--  1 ggm ggm  475 fev 26 20:44 genimage-raspberrypi0w.cfg
gm@gAN515-52:~/embedded-linux/ch6/buildroot ((no branch))$ ll output/images/
total 215132
drwxr-xr-x 3 ggm ggm      4096 fev 26 22:27 ./
drwxrwxr-x 6 ggm ggm      4096 fev 26 21:23 ../
-rwxr-xr-x 1 ggm ggm     28792 fev 26 21:22 bcm2708-rpi-zero-w.dtb*
-rw-r--r-- 1 ggm ggm  33554432 fev 26 22:27 boot.vfat
-rw-r--r-- 1 ggm ggm 125829120 fev 26 22:27 rootfs.ext2
lrwxrwxrwx 1 ggm ggm        11 fev 26 22:27 rootfs.ext4 -> rootfs.ext2
drwxr-xr-x 3 ggm ggm      4096 fev 26 21:09 rpi-firmware/
-rw-r--r-- 1 ggm ggm 159384064 fev 26 22:27 sdcard.img
-rw-r--r-- 1 ggm ggm   6012640 fev 26 21:22 zImage
```

- It is cool to notice that all the `board/raspberrypi*/` folders are actually symlinks to the `board/raspberrypi/` folder
```bash
drwxrwxr-x  2 ggm ggm 4096 fev 26 20:44 raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi0 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi0w -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi2 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi3 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi3-64 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi4 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypi4-64 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypicm4io -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypicm4io-64 -> raspberrypi
lrwxrwxrwx  1 ggm ggm   11 fev 26 20:44 raspberrypizero2w -> raspberrypi
```

- Followed the book examples, applying patches, overlays, calling special scripts at the end of the build process, etc

- I attempted to configure an access point with `raspberrypi0w` wifi and explore buildroot with it, adding systemd, hostapd, etc

- More specifically, I followed [this stack exchange post](https://unix.stackexchange.com/a/448501) but I did not see any success

    - I decided to stop my exploration and jump to yocto because I was either not able to make the access point work (with WPA supplicant config) or not able to build the SW when trying to add systemd / hostapd due to meson, dependencies errors, etc

    - Ex: `ERROR: Dependency "mount" not found`

## Yocto
- 

```bash
```
