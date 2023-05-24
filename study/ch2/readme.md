# 2: Learning about Toolchains

## Thechnical References:


### Building toolchain

- Install linux dependencies:
    ```
    $ sudo apt-get install autoconf automake bison bzip2 cmake \
    flex g++ gawk gcc
    gettext git gperf help2man libncurses5-dev libstdc++6 libtool \
    libtool-bin make
    patch python3-dev rsync texinfo unzip wget xz-utils
    ```

- Clone, build and install crosstool-ng:
    ```bash
    $ git clone https://github.com/crosstool-ng/crosstool-ng.git
    $ cd crosstool-ng
    $ ./bootstrap
    $ ./configure --prefix=${PWD}
    $ make
    $ make install
    ```

- Show help menu: `$ ./ct-ng help`

- There are already pre-built toolchains available: `$ ./ct-ng list-samples`

- Show specific information about one of the samples (toolchains):
    ```bash
    $ ./ct-ng show-arm-cortex_a8-linux-gnueabi
    [L...]   arm-cortex_a8-linux-gnueabi
        Languages       : C,C++
        OS              : linux-6.3
        Binutils        : binutils-2.40
        Compiler        : gcc-12.2.0
        C library       : glibc-2.37
        Debug tools     : duma-2_5_21 gdb-13.1 ltrace-0.7.3 strace-6.2
        Companion libs  : expat-2.5.0 gettext-0.21 gmp-6.2.1 isl-0.26 libelf-0.8.13 libiconv-1.16 mpc-1.2.1 mpfr-4.1.0 ncurses-6.2 zlib-1.2.13 zstd-1.5.5
        Companion tools : autoconf-2.71 automake-1.16.5
    ```

- Open menuconfig to allow for visual configuration of the toolchain: `$ ./ct-ng menuconfig`

- Activate one specific toolchain in the current shell context: `$ ./ct-ng arm-cortex_a8-linux-gnueabi`

- Build the toolchain that is currently activated: `$ ./ct-ng build`

- The built toolchain is in `~/x-tools/arm-cortex_a8-linux-gnueabihf/bin`
    - This is where the applications like the cross compiler is: `$ ll ~/x-tools/arm-cortex_a8-linux-gnueabihf/bin/arm-cortex_a8-linux-gnueabihf-gcc`

- Deactivate the current toolchain in the current shell context: `$ ./ct-ng distclean`
    - Looks like the build directories and all the downloads took ~10GB disk space, whereas the toolchain itself (under ~/x-tools directory) takes only around 500MB

- It is also necessary to compile a toolchain for the QEMU target as well
    - *Is this always the case? Or just when there is no match of the same processor in QEMU?*


### Using toolchain

- Compiling a simple helloworld.c: `$ arm-cortex_a8-linux-gnueabihf-gcc helloworld.c -o helloworld`

- Inspecting the compiled file to know more about it: `file helloworld`

- Inspecting the copiler to know more about the toolchain being used: `$ arm-cortex_a8-linux-gnueabihf-gcc --version`
    - Alternative: `$ arm-cortex_a8-linux-gnueabihf-gcc -v`

- It's also possible to compile for a slightly different CPU like so: `$ arm-cortex_a8-linux-gnueabihf-gcc -mcpu=cortex-a5 helloworld.c -o helloworld`
    - Can list the possible targets with: `$ arm-cortex_a8-linux-gnueabihf-gcc --target-help`
    - You can keep the toolchain always specific and tied to the target architecture OR use one toolchain in a more generic way, just changing the target like shown above. It's a project decision and there is drawbacks and advantages.

- In the case of the example, sysroot directory is at: `$ ll ~/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot`
    - Directory that contains subdirectories for header files, libraries, config files
    - Some of which are used to compile code, some are used in the target device at run time
    - Here are present some of the components fo the C library:
        ```bash
        ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/crosstool-ng (master)$ find  ~/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/ -iname "*libm.*"
        /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/usr/lib/libm.so
        /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/usr/lib/libm.a
        /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/lib/libm.so.6
        ggm@ggm-nitro5:~/Documents/tsmotter/embedded-linux/crosstool-ng (master)$ find  ~/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/ -iname "*librt.*"
        /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/usr/lib/librt.a
        /home/ggm/x-tools/arm-cortex_a8-linux-gnueabihf/arm-cortex_a8-linux-gnueabihf/sysroot/lib/librt.so.1
        ```
    - `libc` is always linked by default to programs but the others have to be explicitly linked with the -l option (excluding the "lib" part of the name, like so: -lm to link libm)
    - To check which libraries have been linked in a target file, do: `$ arm-cortex_a8-linux-gnueabihf-readelf -a myprog | grep "Shared library"`

### Automating the usage of the toolchain
- Script to activate cross-environment:
    ```bash
    PATH=${HOME}/x-tools/arm-cortex_a8-linux-gnueabihf/bin/:$PATH
    export CROSS_COMPILE=arm-cortex_a8-linux-gnueabihf-
    export ARCH=arm
    ```

    - `CROSS_COMPILE` is a makefile variable