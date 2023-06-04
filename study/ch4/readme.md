# 4: Learning about the kernel

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

- menuconfig
    - Configuration utility to go from kconfig files into .config file using an iteractive menu
    - `ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/linux-5.4.50$ make ARCH=arm menuconfig`
    - There are other options (make targets) to deal with kernel configuration
        ```bash
        ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/linux-5.4.50$ make help
        .
        .
        .
        Configuration targets:
        config	  - Update current config utilising a line-oriented program
        nconfig         - Update current config utilising a ncurses menu based program
        menuconfig	  - Update current config utilising a menu based program
        xconfig	  - Update current config utilising a Qt based front-end
        gconfig	  - Update current config utilising a GTK+ based front-end
        oldconfig	  - Update current config utilising a provided .config as base
        ```

## Compiling the kernel

### Issues that happened in my first try:

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

## Booting the kernel
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