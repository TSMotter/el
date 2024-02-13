# 4: Learning about the kernel

- `notifier.py`

    - python tool created to issue a desktop notification whenever a command finishes

    - The desire to build this tool was born after a time that I issued a make command to build the kernel and "Alt + Tabed" back to read the book. The command was finished a long time ago once I actually went back to the command prompt.

    - To use `notifier` do it like this:

        - `ggm@gAN515-52:~/embedded-linux/linux-6.1.31$ notifier make -j12 zImage`

## Thechnical References:

- Linux is actually the kernel

    - The other elements necessary for it to be considered an OS are actually elements from the GNU project (toolchain, C Library, command line tools, etc)

    - The Linux kernel can be combined with the GNU user space to create a GNU/Linux distribution or it can be conbined with an Android user space to create the Android OS (mobile)

    - There are other OSes (like BSD) that combine the User Space + Toolchain + Kernel in a single project

    - The effect of keeping things separated (as is in Linux) is that you gain options in terms of which init system (runit, systemd), C Library (muscl, glibc), package formats (apk, deb), etc to use

- The kernel has 3 main jobs

    - Manage Resources

    - Interface with hardware

    - Provide API to abstract the system for user space programs

        - Main interface between kernel space and user space = C Library

            - C Library: translates user-level functions (those defined in POSIX like read, write, open, clone) into kernel system calls

            - The system calls get handled by a **system call handler**, which will dispatch the call to the specific kernel subsystem (memory manager, filesystem, etc)

            - System calls that require interacting with hardware, will be passed down to a *device driver*

            - Hardware interrupts are always handled by a device driver, never by user space app.

        - Apps. in user space

            - Run in low CPU privilege level

            - Can do very little other than make library calls

            - Pretty much all useful things an user space app. does, is through the kernel, via sys. calls

## Kconfig
- Kernel configuration mechanism

- *KConfig* files "defines" all the possible configuration options, their types, dependencies, default values.

- Are organized as an hierarchy of files

- An example of a *KConfig* configuration option definition:

```KConfig
config DEVMEM
    bool "/dev/mem virtual device support"
    default y
    help
        Say Y here if you want to support the /dev/mem device.
        The /dev/mem device is used to access areas of physical
        memory.
        When in doubt, say "Y".
```

- The configuration items selected are stored in a file called `.config`

- There are several applications that can scan through all KConfig options and produce a `.config` file

    - Some of them will display a menu and allow user to make choices interactively

    - That is the case of `menuconfig`, `xconfig` or `gconfig`

    - To launch `menuconfig`, install de dependencies and use `make` on the target `menuconfig`, like so: `make ARCH=arm menuconfig`

    - If `ARCH` is already defined in the environment of the current shell, you dont need to specify in command line

```bash
ggm@gAN515-52:~/embedded-linux/ $ wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.16.tar.xz
ggm@gAN515-52:~/embedded-linux/ $ tar xf linux-6.6.16.tar.xz
ggm@gAN515-52:~/embedded-linux/ $ mv linux-6.6.16 linux-6.6.16-stable
ggm@gAN515-52:~/embedded-linux/ $ cd linux-6.6.16-stable
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ sudo apt install libncurses5-dev flex bison
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ bbbenv # Source the env. variables
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ echo $ARCH
arm
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ make menuconfig
```

- A *defconfig* file is a working configuration for a specific SoC or group of SoCs

    - It'll contain a colletion "*KConfig* defined configuration options" selected

    - A *defconfig* file will normally specify only configurations that differ from what is default

    - A *defconfig* file is normally a smaller file (couple of hundreds of lines)

    - An example of a *defconfig* entry is: `CONFIG_DEVMEM=y`

    - When working with a vendor suplied kernel, it's common that the vendor will supply a defconfig file

    - To select one of the *defconfigs*, use `make` on the target `*_defconfig`, like so: `make multi_v7_defconfig`

        - This will generate a `.config` file based on that defconfig

- There is also a special `make` target called `oldconfig` which can be useful in 2 scenarios

    - When migrating to a newer kernel version and you want to drop the `.config` that you already use in the previous kernel version

        - In this case, it'll take an existing `.config` file and prompt the user about new configuration options that might have changed, etc so that at the end of the process the `.config` will have been translated to the newed kernel

    - To validate a `.config` that you might have edited manually (out of the context of menuconfig or similar tool)

- The `.config` file contains the actuall configuration that'll be built once we build the kernel

    - The kernel buildsystem will look at whatever is present on `.config` file and produce a `include/generated/autoconf.h` header file that'll contains a `#define` directive for each configuration value so that it'll take effect on the kernel source code at build time

    - This is what will decide if some module is built or not, if it is built as a kernel module or not, the value of some string parameter, etc...

    - An example of a *.config* entry is just like the one in a *defconfig* file: `CONFIG_DEVMEM=y`

## Kernel Modules
- Some of the "*KConfig* defined configuration options" are of type "tristate" which means that they can assume the values "y", "m" or "not defined at all"

- When they are defined as "y" it means that that specific feature will be built into the main kernel image

- When they are defined as "m" it means that that specific feature will be built as a kernel module

- kernel modules are used extensivelly by linux desktop so that the appropriate device and kernel functions are loaded in run time depending on the hardware detected and features required

- The alternative to that would be to build it in the kernel image itself and in that case it'd end up generating an infeasibly large kernel image

- On embedded devices, because the hardware and kernel are usually known at compile time, it's more common to build the features in the kernel image itself (and not as kernel modules)

- Also, using kernel modules create a dependency between kernel and the rootfs (where the modules are present)

- Despite that, there are some situations where using kernel modules might be a great option:

    - When there are proprietary modules (for licensing reasons)

    - To reduce boot time (kernel will not load a bunch of potentially unecessary modules every time)

    - When in fact the device must be prepared for a variety of different external hardwares to be connected to it (just like the case of the desktop)

## Kbuild
- Set of make scripts that take information from `.config` file, workout the dependencies and compile everything necessary to produce kernel image

- The image will contain all the statically linked components, possibly a DTB and one or more kernel modules

- Dependencies are expressed in the makefiles interpoling some definitions with the values from the `.config`

```makefile
obj-y += mem.o random.o
obj-$(CONFIG_TTY_PRINTK) += ttyprintk.o
```

- In this case: 

    - Elements in `obj-y` will be compiled directly into the kernel binary

    - Elements in `obj-m` will be compiled as kernel modules

    - `CONFIG_TTY_PRINTK` can either be defined as "y" or "m" in configuration phase


### Types of kernel images
- Different bootloaders need different types of images to be able to boot them

- Older U-Boot required uImage

- Newer U-Boot can work with zImage (bootz command) 


### building
- Given you have a *.config* file present in the root directory of your kernel source, you can compile a kernel image (with a command such as `make zImage` or `make uImage`)

- Some of the produced files after a build are:

    - `vmlinux`: The kernel as an ELF binary. Most bootloaders will not handle ELF file directly

    - `System.map`: Symbol table in human readable form

    - `Image`: `vmlinux` converted to raw binary

    - `zImage`: compressed `Image`

    - `uImage`: `zImage` + 64-bytes U-Boot header

## Compiling device trees
- To compile device tree(s) use `make` on the target `dtbs`, like so: `make dtbs`

- The compilation uses the device tree compiler (DTC) and produces device tree blobs (DTB)

## Compiling modules
- To compile module(s) use `make` on the target `modules`, like so: `make modules`

- The output will be a bunch of "*.ko" files which can be installed in a custom destination path (most likely the stagin area of the root file system that'll use on the target device later)

    - To do that, use `make` on the target `modules_install`, like so: `make INSTALL_MOD_PATH=$HOME/staging-rootfs modules_install`

## Practical Experiment

### Building a kernel for the BeagleBone Black
```bash
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ bbbenv # Source the env. variables
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ echo $ARCH
arm
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ make mrproper
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ make multi_v7_defconfig
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ make -j`nproc` zImage
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ make -j`nproc` modules
ggm@gAN515-52:~/embedded-linux/linux-6.6.16-stable $ make dtbs
```

- When trying to compile Linux kernel Version 6.6.16, got error due to openssl not available (just like happened when trying to compile U-Boot)

    - Probably would need to re-compile toolchain with openssl included (or compile openssl and include onto current toolchain)

```bash
  HOSTCC  certs/extract-cert
certs/extract-cert.c:21:10: fatal error: openssl/bio.h: No such file or directory
   21 | #include <openssl/bio.h>
      |          ^~~~~~~~~~~~~~~
compilation terminated.
```

- Because my main objective is to reach the yocto / buildroot section of the book, and also because I have already built the kernel using a crosstool-ng generated toolchain before, decided to move forward withou trying to understand how to include openssl into my crosstool-ng generated toolchain (it is not my focus now to debug/strudy about crosstool-ng, I just want to go to yocto part)

### Issues that happened in my first try building the Kernel:

- This was using Linux kernel Version 6.1.31

1. Missing debian certificates:
    - `No rule to make target 'debian/canonical-certs.pem', needed by 'certs/x509_certificate_list'`
    - This issue can be solved either by disabling the signature checkage from the build, or by properly downloading the certificates and making them available to the buildsystem.
    - To disable signature checking:
        ```
        # start the editable menuconfig UI
        make menuconfig

        # Navigate to:
        # Cryptographic API
        #    > Certificates for signature checking
        #       > X.509 certificates to be preloaded into the system blacklist keyring
        # Change the 'debian/certs/debian-uefi-certs.pem' string to ''
        ```
    - To properly download the certificates and make them available:
        - kconfig configurations related to certificates
            ```
            #
            # Certificates for signature checking
            #
            CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"
            CONFIG_MODULE_SIG_KEY_TYPE_RSA=y
            CONFIG_MODULE_SIG_KEY_TYPE_ECDSA=y
            CONFIG_SYSTEM_TRUSTED_KEYRING=y
            CONFIG_SYSTEM_TRUSTED_KEYS="/usr/local/src/debian/canonical-certs.pem"
            CONFIG_SYSTEM_EXTRA_CERTIFICATE=y
            CONFIG_SYSTEM_EXTRA_CERTIFICATE_SIZE=4096
            CONFIG_SECONDARY_TRUSTED_KEYRING=y
            CONFIG_SYSTEM_BLACKLIST_KEYRING=y
            CONFIG_SYSTEM_BLACKLIST_HASH_LIST=""
            CONFIG_SYSTEM_REVOCATION_LIST=y
            CONFIG_SYSTEM_REVOCATION_KEYS="/usr/local/src/debian/canonical-revoked-certs.pem"
            ```
        - Procedure:
            ```
            # end of Certificates for signature checking
            sudo mkdir -p /usr/local/src/debian
            sudo apt install linux-source
            sudo cp -v /usr/src/linux-source-*/debian/canonical-*.pem /usr/local/src/debian/
            sudo apt purge linux-source*
            ```

1. pahole is not available
    ```
    LD      vmlinux.o
    /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/bin//arm-cortex_a8-linux-gnueabihf-ld.bfd: warning: arch/arm/lib/delay-loop.o: missing .note.GNU-stack section implies executable stack
    /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/bin//arm-cortex_a8-linux-gnueabihf-ld.bfd: NOTE: This behaviour is deprecated and will be removed in a future version of the linker
    MODPOST vmlinux.o
    MODINFO modules.builtin.modinfo
    BTF: .tmp_vmlinux.btf: pahole (pahole) is not available
    Failed to generate BTF for vmlinux
    Try to disable CONFIG_DEBUG_INFO_BTF
    make: *** [Makefile:1080: vmlinux] Error 1
    ```
    - pahole shows data structure layouts encoded in debugging information formats, DWARF and CTF being supported.
        - This is useful for, among other things: optimizing important data structures by reducing its size, figuring out what is the field sitting at an offset from the start of a data structure, investigating ABI changes and more generally understanding a new codebase you have to work with.
        - `sudo apt install pahole`

### Booting the kernel
```log
U-Boot SPL 2021.01 (May 22 2023 - 16:26:36 -0300)
Trying to boot from MMC1


U-Boot 2021.01 (May 22 2023 - 16:26:36 -0300)

CPU  : AM335X-GP rev 2.1
Model: TI AM335x BeagleBone Black
DRAM:  512 MiB
WDT:   Started with servicing (60s timeout)
NAND:  0 MiB
MMC:   OMAP SD/MMC: 0, OMAP SD/MMC: 1
Loading Environment from FAT... *** Warning - bad CRC, using default environment

<ethaddr> not set. Validating first E-fuse MAC
Net:   eth2: ethernet@4a100000, eth3: usb_ether
Hit any key to stop autoboot:  0
=>
=>
=>
=>
=> fatload mmc 0:1 0x80200000 zImage
10387968 bytes read in 667 ms (14.9 MiB/s)
=> fatload mmc 0:1 0x80f00000 am335x-boneblack.dtb
69937 bytes read in 9 ms (7.4 MiB/s)
=> setenv bootargs console=ttyO0,115200
=> bootz 0x80200000 - 0x80f00000
## Flattened Device Tree blob at 80f00000
   Booting using the fdt blob at 0x80f00000
   Loading Device Tree to 8ffeb000, end 8ffff130 ... OK

Starting kernel ...
.
.
.
[    3.471946] Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
[    3.480258] CPU: 0 PID: 1 Comm: swapper/0 Not tainted 6.1.31 #1
[    3.486217] Hardware name: Generic AM33XX (Flattened Device Tree)
[    3.492358]  unwind_backtrace from show_stack+0x10/0x14
[    3.497661]  show_stack from dump_stack_lvl+0x40/0x4c
[    3.502769]  dump_stack_lvl from panic+0x108/0x350
[    3.507620]  panic from mount_block_root+0x174/0x20c
[    3.512648]  mount_block_root from prepare_namespace+0x150/0x18c
[    3.518712]  prepare_namespace from kernel_init+0x18/0x12c
[    3.524253]  kernel_init from ret_from_fork+0x14/0x2c
[    3.529349] Exception stack(0xe0009fb0 to 0xe0009ff8)
[    3.534435] 9fa0:                                     00000000 00000000 00000000 00000000
[    3.542660] 9fc0: 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
[    3.550883] 9fe0: 00000000 00000000 00000000 00000000 00000013 00000000
[    3.557550] ---[ end Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0) ]---
```

## Kernel Panic and Early user space
- Occurs when the kernel finds an unrecoverable error

- Kernel is useless without a user space to control it... It'll issue a kernel panic

- A user can be provided to the kernel via ramdisk OR a mountable mass storage device

- During initialization, the control is switched from kernel to user space at some point

    - For this to happen, the kernel has to mount a rootfs and execute a program in that rootfs

    - If there is a ramdisk, it'll try to execute `/init` (which will set up the user space)

    - If there is no ramdisk, it'll try to mount a filesystem based on a block device specified via kernel command line (`root=/dev/<disk_name>[p]<partition_number>`), where [p] is present in case of SD card and eMMC

    - If the mount is successful, the kernel will try to execute /sbin/init, /etc/init, /bin/init, /bin/sh (stoping at the first one that works)

    - The program executed by the kernel can be changed via kernel command line (for ramdisk set `rdinit=`, for filesystem set `init=`)

## Kernel command line
- String passed to the kernel by the bootloader via `bootargs` variable (in the case of U-Boot)

    - Alternativelly, it can be defined in the DT or in the kernel configuration, via option `CONFIG_CMDLINE`

- There is a list of parameters that can be set this way

## Extra information
- Busy-box
    - BusyBox is a software package that provides a collection of commonly used Unix utilities in a single executable file. It is designed to be small and lightweight, making it well-suited for embedded systems or resource-constrained environments.

    - BusyBox includes a variety of command-line tools such as file manipulation utilities (e.g., ls, cp, mv), shell utilities (e.g., echo, grep, sed), and system administration utilities (e.g., ifconfig, init, mount). These tools are typically found in the user space of an operating system, which is the part of the system where user applications and utilities run.

    - When BusyBox is used in an embedded system or other resource-limited environment, it allows for a more efficient use of system resources. By using a shared set of libraries and binaries, the overall system size can be minimized

- **.apk versus .deb**
    - APK and DEB are file formats used for packaging and distributing software on different operating systems. Here are some key differences between them:

    - Operating Systems:
        - **APK:** APK (Android Package) is primarily used for distributing applications on the Android operating system. It is the standard package format for Android apps.
        - **DEB:** DEB (Debian Package) is used in Debian-based Linux distributions such as Debian, Ubuntu, and their derivatives. It is the standard package format for software installation on these systems.

    - File Format:
        - **APK:** APK files are essentially compressed archives that contain all the necessary files and resources required for an Android application, including code (compiled or interpreted), assets, libraries, and manifest files.
        - **DEB:** DEB files are ar archives that consist of control files and package metadata along with the application files to be installed. The control files contain information about the package dependencies, version, maintainer, and other package-specific details.

    - Package Management:
        - **APK:** Android uses the Google Play Store as the primary distribution platform for APK files. Users can also install APK files directly on their devices from third-party sources.
        - **DEB:** Debian-based Linux distributions use package managers like APT (Advanced Package Tool) to handle software installation, updates, and dependency resolution. DEB files are typically downloaded and installed through package managers or software centers.
