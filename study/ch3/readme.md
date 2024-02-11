# 3: Learning about Bootloaders

## Thechnical References:
- Bootloader has 2 main functionalities:

    - Initialize the system in a basic level (only as much of the system as is necessary to load the kernel)

        - When the system boots (or resets) the memory controllers are not set up, so those storage is not available

        - The system bootstrap process consists of several phases, each bring up more of the hardware

    - Load the kernel into RAM and create execution environment for it

        - The interface between bootloader and kernel will contain at least:

            - A pointer to a structure containing information about the HW

                - At the very least, size and location of the physical RAM, as well as CPU clock speed

                - Previously this was done via a "board information structure" for Power PC, or via a list of "A tags" for ARM

                - Either way, the amount of information was very limited, leaving the bulk of information to either: be discovered in run time OR hard coded into the kernel (called platform data)

                - This meant that each different board/device/platform had to had a kernel compiled specifically for it (due to differences in platform data)

                - This was bad and it was the motivator for the introduction of **Device Tree**

                - Now, a single kernel binary can run on a wide range of different platforms

            - A kernel command line (text file (plain ASCII string) that controls the behavior of linux)

                - Contains, for example, the name of the device that contains the rootfs

- Additionally, the bootloader must also provide a maintenance mode for:

    - Updating boot configurations 

    - Loading new boot images

    - Maybe running diagnostics

- The book goes through what are the intermediate steps of a boot sequence (ROM code, SPL, TPL, kernel)



## U-boot
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
```bash
ggm@gAN515-52:~/embedded-linux/u-boot ((HEAD detached at v2021.01))$ ll configs/am335x_
am335x_baltos_defconfig           am335x_hs_evm_defconfig           am335x_shc_ict_defconfig
am335x_boneblack_vboot_defconfig  am335x_hs_evm_uart_defconfig      am335x_shc_netboot_defconfig
am335x_evm_defconfig              am335x_igep003x_defconfig         am335x_shc_sdboot_defconfig
am335x_evm_spiboot_defconfig      am335x_pdu001_defconfig           am335x_sl50_defconfig
am335x_guardian_defconfig         am335x_shc_defconfig 
```

- Relevant commands
```bash
# .bashrc function to source cross compiling variables and load toolchain to path
ggm@gAN515-52:~/embedded-linux $ bbbenv
ggm@gAN515-52:~/embedded-linux $ git clone git://git.denx.de/u-boot.git
ggm@gAN515-52:~/embedded-linux $ cd u-boot
ggm@gAN515-52:~/embedded-linux/u-boot (master)$ git checkout v2021.01
ggm@gAN515-52:~/embedded-linux/u-boot ((HEAD detached at v2021.01))$ make clean
ggm@gAN515-52:~/embedded-linux/u-boot ((HEAD detached at v2021.01))$ make distclean
ggm@gAN515-52:~/embedded-linux/u-boot ((HEAD detached at v2021.01))$ make am335x_evm_defconfig
ggm@gAN515-52:~/embedded-linux/u-boot ((HEAD detached at v2021.01))$ make
```

- Tried compiling on tag v2024.01 but got error due to openssl not available

    - Probably would need to re-compile toolchain with openssl included (or compile openssl and include onto current toolchain)

    - Decided to just go with v2021.01...

- The output of the build will contain:

    - u-boot: U-Boot in ELF object format, suitable for use with a debugger

    - u-boot.map: The symbol table

    - u-boot.bin: U-Boot in raw binary format, suitable for running on your device

    - u-boot.img: This is u-boot.bin with a U-Boot header added, suitable for uploading to a running copy of U-Boot

    - u-boot.srec: U-Boot in Motorola S-record (SRECORD or SRE) format, suitable for transferring over a serial connection

45    - MLO: The secondary program loader (SPL)

- Using the available script to format the SD card:
```bash
ggm@gAN515-52:~/embedded-linux/Mastering-Embedded-Linux-Programming-Third-Edition$ ./format-sdcard.sh mmcblk0
```

- Checking the SD card partitions and filesystem format:
```bash
ggm@gAN515-52:~/embedded-linux/Mastering-Embedded-Linux-Programming-Third-Edition (master)$ df -T /dev/mmcblk0p1
Filesystem     Type 1K-blocks  Used Available Use% Mounted on
/dev/mmcblk0p1 vfat     65390     0     65390   0% /media/ggm/boot
ggm@gAN515-52:~/embedded-linux/Mastering-Embedded-Linux-Programming-Third-Edition (master)$ df -T /dev/mmcblk0p2
Filesystem     Type 1K-blocks  Used Available Use% Mounted on
/dev/mmcblk0p2 ext4    996780    24    927944   1% /media/ggm/rootfs
```

- U-Boot does not have a file system, so the way it tracks content and manage image files is through a 64-byte header on the files

- The `mkimage` command line tool can be used to "prepare" images to be usable by U-Boot:

    - It is a utility present on U-Boot repository itself which can be compiled with

        - `gggm@gAN515-52:~/embedded-linux/u-boot ((HEAD detached at v2021.01))$ make tools`

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

- When the U-Boot boots, it'll give you a shell where you can type commands

- By default, it'll not perform any actions, like booting a kernel image

- To boot a kernel image, you should either send a series of commands manually, to inform the medium where the image can be found, the address in RAM in which to load that image, etc

    - U-Boot commands like `fatload` can be used to load an image from an attached interfacec (like eMMC card) or `tftp` + `tftpboot` can be used to load an image from a network IP using FTP 

    - U-Boot command `bootm` can then be used to boot the image previously loaded in memory

- Issuing a series o commands every time the system boots is not practical and there is a way to automate it with U-Boot scripts

    - If a special U-Boot environment variable (`bootcmd`) contains a script, it is run at power-up after `bootdelay` seconds

    - `bootdelay` can be interrupted to enter the U-Boot interactive terminal

    - Example of `bootcmd` command:

        - `setenv bootcmd nand read 82000000 400000 200000\;bootm 82000000`