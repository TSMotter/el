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
- Not only can build toolchain, bootloader, kernel and rootfs, but a "complete linux distribution", with binary packages that can be installed at runtime

- Characteristics of the build system:

    - Structured around recipes (a combination of Python and shell script)

    - One of the main pillars is the task scheduler: BitBake

### History
- In 2003 OpenEmbedded (OE) comes to life as a build system for handheld computers, able to create binary packages and combine them in different ways based on the metadata provided in a very versatile waty

- In 2005 Poky was created by OpenHand as a fork of OpenEmbedded but with a more conservative choice of packages and with releases stable over a period of time

- In 2008 Intel bought OpenHand

- In 2010 Intel transferred Poky to the Linux Foundation and created the Yocto Project

- Since 2010, the common parts of the OpenEmbedded and Poky have been combined into a project known as OpenEmbedded Core (OE-Core)

- Main components of the Yocto Project:

    - OE-Core: Core metadata (shared with OpenEmbedded)

    - BitBake: Task scheduler (shared with OpenEmbedded and other projects)

    - Poky: Reference distribution

### Stable Releases
- Usually every 6 months there is a new release

- Each release has it's code name

- Each release is supported for 12 months

- TLS releases is supported for 2 years


### Working with Yocto
- Clone it

```bash
ggm@gAN515-52:~/embedded-linux/ch6 $ git clone -b dunfell git://git.yoctoproject.org/poky.git
```

- Initialize the environment by sourcing the script (should be done every time that will work)

    - This will create the working directory (by default: `build`)

    - This directory is where intermediate and final target files will be placed, as well as configurations about the build

```bash
ggm@gAN515-52:~/embedded-linux/ch6/poky (dunfell)$ source oe-init-build-env
```

- One very important sub directory is `build/conf`, which will contain build configuration files

    - `local.conf`: Specification of the device you are building for and build environment

    - `bblayers.conf`: paths to the meta layers

- Set the MACHINE variable in `build/conf/local.conf` by uncommenting

- In order to build an image, need to tell bitbake what to build

    - bitbake accepts as parameter a task and a recipe or a target

    - bitbake will execute the specified task for the given set of target / recipes

    - The default task is "build" (do_build)

    - It is possible to list the tasks for a specific target

        - Example: `bitbake -c listtasks core-image-minimal`

    - `listtasks` itself is a task

    - `core-image-minimal` is a recipe (target) (`poky/meta/recipes-core/images/core-image-minimal.bb`)

    - Example of other tasks:

        - do_build, do_clean, do_cleanall, do_compile, do_configure, do_install, do_package, do_populate_sdk, do_rootfs

### Layers
- Yocto metadata is structured into layers

- Each layer starts wih "meta-" in the name

- The main layers are:

    - meta: OpenEmbedded core

    - meta-poky: Metadata specific for the poky distribution

    - meta-yocto-bsp: Contains the board support package for the devices (MACHINEs) supported by Yocto

- Layers are shared as repositories containing related sets of instructions which tell the build system what to do

- Layer have an override capability (which is what allows you to customize previous collaborative or community supplied layers to suit your product requirements)

- As an example, you could have a BSP layer, a GUI layer, a distro configuration, middleware, or an application

- Use BSP layers from silicon vendors when possible

- The list of layers which bitbake will search for recipes is stored in `<your build directory>/conf/bblayers.conf`

    - Example: `poky/build/conf/bblayers.conf`

- A list of layers can be searched in the layers index

    - http://layers.openembedded.org/layerindex/

- Adding a layer is as simple as adding the **meta-** directory to a suitable location and editing the bblayers.conf file

    - When adding a new layer, take care with the dependencies that the new layer have as well as the compatibility with the Yocto version

### Creating a layer

```bash
ggm@ubuntu2004:~/embedded-linux/poky (dunfell)$ bitbake-layers create-layer meta-tsmotter
NOTE: Starting bitbake server...
Add your new layer with 'bitbake-layers add-layer meta-tsmotter'
ggm@ubuntu2004:~/embedded-linux/poky (dunfell)$ cd build/
ggm@ubuntu2004:~/embedded-linux/poky/build (dunfell)$ bitbake-layers add-layer ../meta-tsmotter
NOTE: Starting bitbake server...
ggm@ubuntu2004:~/embedded-linux/poky/build (dunfell)$ cat conf/bblayers.conf | grep tsm
  /home/ggm/embedded-linux/poky/meta-tsmotter \
```

## Getting information about a yocto variable
- Example inspecting what is the value of the variable `IMAGE_ROOTFS` for the target `core-image-minimal`
```bash
ggm@ubuntu2004:~/embedded-linux/poky/build (dunfell)$ bitbake-getvar -r core-image-minimal IMAGE_ROOTFS
#
# $IMAGE_ROOTFS [2 operations]
#   set /home/ggm/embedded-linux/poky/meta/conf/bitbake.conf:456
#     "${WORKDIR}/rootfs"
#   set /home/ggm/embedded-linux/poky/meta/conf/documentation.conf:222
#     [doc] "The location of the root filesystem while it is under construction (i.e. during do_rootfs)."
# pre-expansion value:
#   "${WORKDIR}/rootfs"
IMAGE_ROOTFS="/home/ggm/embedded-linux/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/core-image-minimal/1.0-r0/rootfs"
```
- Less verbose:
```bash
ggm@ubuntu2004:~/embedded-linux/poky/build (dunfell)$ bitbake-getvar -r core-image-minimal --value IMAGE_ROOTFS
/home/ggm/embedded-linux/poky/build/tmp/work/beaglebone_yocto-poky-linux-gnueabi/core-image-minimal/1.0-r0/rootfs
```

- Other examples
```bash
ggm@ubuntu2004:~/embedded-linux/poky/build (dunfell)$ bitbake-getvar -r software-timer --value S
/home/ggm/embedded-linux/poky/build/tmp/work/cortexa8hf-neon-poky-linux-gnueabi/software-timer/0.1+gitAUTOINC+5d8327406d-r0/git
ggm@ubuntu2004:~/embedded-linux/poky/build (dunfell)$ bitbake-getvar -r software-timer --value B
/home/ggm/embedded-linux/poky/build/tmp/work/cortexa8hf-neon-poky-linux-gnueabi/software-timer/0.1+gitAUTOINC+5d8327406d-r0/build
```

### Recipes
- Recipes are one amongst many other types of metadata that bitbake processes:

    - Recipes:

        - File ending in ".bb"

        - Contains information about building a unit of SW, including how to get the source code, dependencies, how to build and install it

    - Append:

        - File ending in ".bbappend"

        - Allow some detail of a recipe to be overwritten or extended

        - It'll simply append it's instructions to the end of the corresponding ".bb" file

    - Include:

        - File ending in ".inc"

        - Contains information that is common to multiple recipes (allow information to be shared)

        - These files may be included using `include` (does NOT produce an error if file does NOT exists) or `require` (produces an error if file does NOT exists) keyword

    - Classes:

        - File ending in ".bbclass"

        - Contains common build information, example: how to build a kernel or autotools

        - Classes are inherited and extended in other classes and recipes using the `inherit` keyword

        - The `classes/base.bbclass` class is implicitly inherited in every recipe

    - Configuration:

        - File ending in ".conf"

        - Contains configurations that control the build process

- Recipes are a collection of tasks

- Written in a combination of Python and shell

- bitbake is used to execute such tasks

- The book goes over the creation of a custom recipe for building and installing a helloworld program into the final image. The recipe is created in the meta-nova layer

- The list of packages to be installed is held in a variable named `IMAGE_INSTALL`

- It is possible to add packages via the use of the variable `IMAGE_INSTALL_append`

    - For example, it's possible to add `IMAGE_INSTALL_append = " helloworld"` to the end of the `conf/local.conf`

    - If you look at `tmp/deploy/images/beaglebone-yocto/core-image-minimal-beaglebone-yocto.tar.bz2` you'll see `/usr/bin/helloworld` binary

- There is another varible that allow for more customization of the final image, that is the `EXTRA_IMAGE_FEATURES`

    - Some example of available options are: X server, read-only fs, debug symbols for packages, allow root login without passwords, etc

### Image Recipe
- Editing local.conf to change the image configuration is an option but falls short when you want to share the work with others, etc

- This is when image recipes come in hand

- An image recipe will contain information about how to create an image for the given target, including information about bootloader, kernel, rootfs, etc

- By default image recipes are put in the `images` directory

    - Example: `poky/meta/recipes-core/images/core-image-minimal.bb`

    - To get a full list: `ls meta*/recipes*/images/*.bb`

- Example creating an image recipe that is based on `core-image-minimal.bb` (includes it via the `require` keyword) and extend the packages installed

```bash
ggm@gAN515-52:~/embedded-linux/ch6/poky (dunfell)$ cat meta-nova/recipes-local/images/nova-image.bb
require recipes-core/images/core-image-minimal.bb
IMAGE_INSTALL += "helloworld strace"
ggm@gAN515-52:~/embedded-linux/ch6/poky (dunfell)$ bitbake nova-image
```

### Creating an SDK
- The following command will generate a stand alone installable SDK, which can be shared between people
```bash
ggm@gAN515-52:~/embedded-linux/ch6/poky (dunfell)$ bitbake -c populate_sdk nova-image
```

- The result is a self-installing bash scrip

```bash
ggm@gAN515-52:~/embedded-linux/ch6/poky (dunfell)$ poky-glibc-x86_64-nova-image-cortexa8hf-neon-beaglebone-yocto-toolchain-3.1.5.sh
```

- Alternativelly, if you just want a simple toolchain with just C/C++ cross-compiler, you can use the following recipe: `poky/meta/recipes-core/meta/meta-toolchain.bb`

    - `bitbake meta-toolchain`

- You'll be able to compile and work stand alone like this:

    - `$CC -O helloworld.c -o helloworld`
