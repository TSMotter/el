# 3: Learning about Bootloaders

## Thechnical References:

### U-boot

- From u-boot readme:
    ```
    If you are not using a native environment, it is assumed that you
    have GNU cross compiling tools available in your path. In this case,
    you must set the environment variable CROSS_COMPILE in your shell.
    Note that no changes to the Makefile or any other source files are
    necessary. For example using the ELDK on a 4xx CPU, please enter:

        $ CROSS_COMPILE=ppc_4xx-
        $ export CROSS_COMPILE

    U-Boot is intended to be simple to build. After installing the
    sources you must configure U-Boot for one specific board type. This
    is done by typing:

        make NAME_defconfig

    where "NAME_defconfig" is the name of one of the existing configu-
    rations; see configs/*_defconfig for supported names.
    ```

    - This is intended to be built after activating the cross compilation environment as tougth in Chapter 02
    - `CROSS_COMPILE` is a makefile variable

- These are the possible options of configurations for the `am335x` family:
    ```
    gm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/u-boot ((v2021.01))$ ll configs/am335x_
    am335x_baltos_defconfig           am335x_hs_evm_defconfig           am335x_shc_ict_defconfig
    am335x_boneblack_vboot_defconfig  am335x_hs_evm_uart_defconfig      am335x_shc_netboot_defconfig
    am335x_evm_defconfig              am335x_igep003x_defconfig         am335x_shc_sdboot_defconfig
    am335x_evm_spiboot_defconfig      am335x_pdu001_defconfig           am335x_sl50_defconfig
    am335x_guardian_defconfig         am335x_shc_defconfig 
    ```

- Using the available script to format the SD card:
    ```
    ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/Mastering-Embedded-Linux-Programming-Third-Edition$ ./format-sdcard.sh mmcblk0
    ```

- Checking the SD card partitions and filesystem format:
    ```
    ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/Mastering-Embedded-Linux-Programming-Third-Edition (master)$ df -T /dev/mmcblk0p1
    Filesystem     Type 1K-blocks  Used Available Use% Mounted on
    /dev/mmcblk0p1 vfat     65390     0     65390   0% /media/ggm/boot
    ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/Mastering-Embedded-Linux-Programming-Third-Edition (master)$ df -T /dev/mmcblk0p2
    Filesystem     Type 1K-blocks  Used Available Use% Mounted on
    /dev/mmcblk0p2 ext4    996780    24    927944   1% /media/ggm/rootfs
    ```

- The `mkimage` command line tool:
    - Utility provided by U-Boot that enables the creation of bootable images in a format that U-Boot can understand.
        - Compilation: `ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/u-boot ((v2021.01))$ make tools
`
    - These bootable images can be:
        - the U-Boot bootloader itself
        - device tree files
        - kernel images
        - initial RAM disk (initrd)
        - configuration settings
    - This tool plays a vital role in the bootstrapping process of embedded Linux systems using U-Boot.
    - Main formats are:
        - `U-Boot Legacy format:` This format is used by older versions of U-Boot and involves concatenating the U-Boot SPL (Secondary Program Loader), U-Boot proper, and other components into a single binary image.
        - `U-Boot FIT (Flattened Image Tree) format:` This format is based on the device tree concept
    - Example: `mkimage -A arm -O linux -T kernel -C gzip -a 0x80008000 -e 0x80008000 -n 'Linux' -d zImage uImage`
        - the architecture is arm 
        - the operating system is linux
        - the image type is kernel
        - the compression scheme is gzip
        - the load address is 0x80008000
        - the entry point is the same as the load address
        - the image name is Linux
        - the image datafile is named zImage
        - the image being generated is named uImage