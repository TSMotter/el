# Case 1
- `ERROR: do_package_qa: QA Issue: package <packagename> contains bad RPATH <rpath> in file <file> [rpaths]`

## References
- https://docs.yoctoproject.org/3.1.5/ref-manual/ref-qa-checks.html#errors-and-warnings
- https://gitlab.kitware.com/cmake/community/-/wikis/doc/cmake/RPATH-handling
- https://stackoverflow.com/a/45843676

## Description, development, solution
- Initiative:
    - build and install a proprietary shared library (.so) file
    - build and install an app that uses that shared library
    - Make the proprietary library available in the SDK so that stand alone apps that use it, can be developed

- To do this, I'm using the following proprietary repository:
    - [TSMotter/software-timer](https://github.com/TSMotter/software-timer)

- The `software-timer` repository contains 2 main folders:
    - `lib`
        - This contains the code that will generate the shared library (.so) file
    - `example`
        - This contains the code of an example app, that uses the shared library (.so) file

- It is possible to see during compilation of the `software-timer` that the shared library (.so) file gets generated into the `/build/lib` folder

```bash
ggm@ubuntu2004:~/tsmotter/software-timer(master)$ ll build/lib/ | grep so
lrwxrwxrwx 1 ggm ggm    16 nov  1 07:56 libgm_timer.so -> libgm_timer.so.0*
lrwxrwxrwx 1 ggm ggm    18 nov  1 07:56 libgm_timer.so.0 -> libgm_timer.so.0.1*
-rwxrwxr-x 1 ggm ggm 16328 nov  1 07:56 libgm_timer.so.0.1*
```

- At the same time, the example app binary will be available at

```bash
ggm@ubuntu2004:~/tsmotter/software-timer(master)$ ll build/main
-rwxrwxr-x 1 ggm ggm 17120 nov  1 07:56 build/main*
```

- At the yocto level, there is the following recipe, that fetches source from github:
    - [meta-motter/recipes-local/software-timer/software-timer_git.bb](https://github.com/TSMotter/meta-motter/blob/master/recipes-local/software-timer/software-timer_git.bb)

- When *bitbaking* this recipe, I got the error in question here...
```bash
Initialising tasks: 100% |###############################################################################################################################################################################| Time: 0:00:00
Sstate summary: Wanted 7 Local 0 Mirrors 0 Missed 7 Current 131 (0% match, 94% complete)
NOTE: Executing Tasks
ERROR: software-timer-from-gitAUTOINC+4fe0ce98b8-r0 do_package_qa: QA Issue: package software-timer contains bad RPATH /home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/build/lib in file /home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/packages-split/software-timer/usr/bin/software-timer [rpaths]
ERROR: software-timer-from-gitAUTOINC+4fe0ce98b8-r0 do_package_qa: QA Issue: /usr/bin/software-timer contained in package software-timer requires libgm_timer.so.0, but no providers found in RDEPENDS:software-timer? [file-rdeps]
ERROR: software-timer-from-gitAUTOINC+4fe0ce98b8-r0 do_package_qa: Fatal QA errors were found, failing task.
ERROR: Logfile of failure stored in: /home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/temp/log.do_package_qa.26327
ERROR: Task (/home/ggm/embedded-linux/sublime-platform/build/../meta-motter/recipes-local/software-timer/software-timer_git.bb:do_package_qa) failed with exit code '1'
NOTE: Tasks Summary: Attempted 566 tasks of which 551 didn't need to be rerun and 1 failed.

Summary: 1 task failed:
  /home/ggm/embedded-linux/sublime-platform/build/../meta-motter/recipes-local/software-timer/software-timer_git.bb:do_package_qa
Summary: There were 3 ERROR messages, returning a non-zero exit code.
ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ Connection to 127.1.0.1 closed by remote host.
Connection to 127.1.0.1 closed.
```

- Studying, it was possible to understand better about what `RPATH` and `RUNPATH` actually means

- The `RPATH` or `RUNPATH` of an executable or shared library is an **OPTIONAL** entry in the `.dynamic` section of the ELF executable

- It is a "Run-time search path" that is hardcoded in the ELF executable

- Dynamic loaders will use this path to find the required libraries dynamically

- There is traditionally an hierarchy of search places:
    - `RPATH` - a list of directories which is linked into the executable, supported on most UNIX systems. It is ignored if `RUNPATH` is present.
    - `LD_LIBRARY_PATH` - an environment variable which holds a list of directories
    - `RUNPATH` - same as RPATH, but searched after `LD_LIBRARY_PATH`, supported only on most recent UNIX systems, e.g. on most current Linux systems
    - `/etc/ld.so.conf` - configuration file for ld.so which lists additional library directories
    - builtin directories - basically `/lib` and `/usr/lib`

- It is possible to inspect an ELF to check some information
    - The `RPATH` of a given binary can be checked using the `objdump` utility with the `-x` option:

- On the host environment, it looks like this:
```bash
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ file build/main 
build/main: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=d9d3516ea4e8e784a956afa42f3142dc2eab3947, for GNU/Linux 3.2.0, not stripped

ggm@ubuntu2004:~/tsmotter/software-timer (master)$ objdump -x build/main | grep PATH -C 4

Dynamic Section:
  NEEDED               libgm_timer.so.0
  NEEDED               libc.so.6
  RUNPATH              /home/ggm/tsmotter/software-timer/build/lib
  INIT                 0x0000000000001000
  FINI                 0x0000000000001458
  INIT_ARRAY           0x0000000000003d58
  INIT_ARRAYSZ         0x0000000000000008
```

- On the bitbake build directory, it looks like this:
```bash
ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ file /home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/packages-split/software-timer/usr/bin/software-timer
/home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/packages-split/software-timer/usr/bin/software-timer: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-armhf.so.3, BuildID[sha1]=9ae96d5fae649e88bffbf3daf02e8ba823e7860d, for GNU/Linux 3.2.0, stripped

ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ objdump -x /home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/packages-split/software-timer/usr/bin/software-timer | grep PATH -C 4

Dynamic Section:
  NEEDED               libgm_timer.so.0
  NEEDED               libc.so.6
  RPATH                /home/ggm/embedded-linux/sublime-platform/build/tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+4fe0ce98b8-r0/build/lib
  INIT                 0x00010540
  FINI                 0x00010790
  INIT_ARRAY           0x00020f00
  INIT_ARRAYSZ         0x00000004
```

- It is possible now to understand what the error means...

- The error is indicating that there is a hardcoded `RPATH` in a produced (and to be installed) app ELF

- This `RPATH` is valid on the host environment where the app was compiled and where the shared library is present, but would not be valid on the target

- Let us discuss some options now...

## Option 1 - Completely remove the RPATH from the compiled ELF
- Since the `RPATH` is an optional field, it can be completely removed the produced ELF
    - In this case, the linker/loader will search for the run time dependencies in the default paths of the system

- The problem with completely removing the `RPATH` is that when you are developing an continuosly compiling/running the application from within the `<app>/build` directory, if there is no `RPATH` in the produced ELF, the system will try to find the shared library in the system's default paths

- Because you did not install the library on the system, it will not find it and you will not be able to execute the app ELF from within it's build directory

- There is a better option...

## Option 2 - Remove the RPATH from the compiled ELF only in it's installation process
- cmake allows a very flexible control over the `RPATH` with the following target options:
```bash
# Global setup for the project
CMAKE_SKIP_BUILD_RPATH
CMAKE_BUILD_WITH_INSTALL_RPATH
CMAKE_INSTALL_RPATH
CMAKE_INSTALL_PREFIX
CMAKE_INSTALL_RPATH_USE_LINK_PATH
CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES

# Example:
set(CMAKE_SKIP_BUILD_RPATH FALSE)

# Specific setup for single targets
SKIP_BUILD_RPATH
BUILD_WITH_INSTALL_RPATH
INSTALL_RPATH
INSTALL_PREFIX
INSTALL_RPATH_USE_LINK_PATH
PLATFORM_IMPLICIT_LINK_DIRECTORIES

# Example:
set_target_properties(main PROPERTIES SKIP_BUILD_RPATH FALSE)
```

- This allows us to configure specific behavior for the `RPATH` property given whether it is within the build directory of the app or whether it is being installed

- The changes made are as follows:
- Changes in `example/CMakeLists.txt`:
    - Use, i.e. don't skip the full `RPATH` for the build tree
        - `set_target_properties(main PROPERTIES SKIP_BUILD_RPATH FALSE)`
    - When building, don't use the install `RPATH` already (but later on when installing)
        - `set_target_properties(main PROPERTIES BUILD_WITH_INSTALL_RPATH FALSE)`
    - The `RPATH` to be used when installing (empty, so that loader will search in standard paths like `/usr/lib`)
        - `set_target_properties(main PROPERTIES INSTALL_RPATH "")`
    - Don't add the automatically determined parts of the `RPATH` which point to directories outside the build tree to the install RPATH
        - `set_target_properties(main PROPERTIES INSTALL_RPATH_USE_LINK_PATH FALSE)`
    - Define installation rule for the produced ELF
        - `install(TARGETS main ${CMAKE_INSTALL_BINDIR})`

- Changes in `lib/CMakeLists.txt`:
    - Define installation rule for the produced shared library
        - `install(TARGETS gm_timer ${CMAKE_INSTALL_LIBDIR})`

### Tests on host machine
- There is an `RPATH` in the ELF within the build tree, but there isn't one in the ELF that is installed
- I'm able to continue using the produced ELF within the build directory, but if I try to run the ELF from the installation directory, it'll complain about missing libraries (as expected)
```bash
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ mkdir mockinstall
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ export DESTDIR=$(pwd)/mockinstall
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ echo $DESTDIR
/home/ggm/tsmotter/software-timer/mockinstall
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ ./bbuild.sh -r example
/* ... */
[100%] Built target main
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ cmake --install build --strip
-- Install configuration: ""
-- Installing: /home/ggm/tsmotter/software-timer/mockinstall/usr/local/lib/libgm_timer.so.0.1
-- Installing: /home/ggm/tsmotter/software-timer/mockinstall/usr/local/lib/libgm_timer.so.0
-- Installing: /home/ggm/tsmotter/software-timer/mockinstall/usr/local/lib/libgm_timer.so
-- Installing: /home/ggm/tsmotter/software-timer/mockinstall/usr/local/bin/main
-- Set runtime path of "/home/ggm/tsmotter/software-timer/mockinstall/usr/local/bin/main" to ""
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ file build/main
build/main: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=87b7fab6ae724cfade5ed2e4a7a96d48aca52e4e, for GNU/Linux 3.2.0, not stripped
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ file mockinstall/usr/local/bin/main
mockinstall/usr/local/bin/main: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=87b7fab6ae724cfade5ed2e4a7a96d48aca52e4e, for GNU/Linux 3.2.0, stripped
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ objdump -x build/main | grep PATH
  RUNPATH              /home/ggm/tsmotter/software-timer/build/lib:
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ objdump -x mockinstall/usr/local/bin/main | grep PATH
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ du -h build/main
20K     build/main
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ du -h mockinstall/usr/local/bin/main
16K     mockinstall/usr/local/bin/main
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ file build/lib/libgm_timer.so.0.1
build/lib/libgm_timer.so.0.1: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=9568b7039085d69a4e060ccccd8201a107177709, not stripped
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ file mockinstall/usr/local/lib/libgm_timer.so.0.1
mockinstall/usr/local/lib/libgm_timer.so.0.1: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=9568b7039085d69a4e060ccccd8201a107177709, stripped
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ du -h build/lib/libgm_timer.so.0.1
16K     build/lib/libgm_timer.so.0.1
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ du -h mockinstall/usr/local/lib/libgm_timer.so.0.1
16K     mockinstall/usr/local/lib/libgm_timer.so.0.1
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ ./build/main

 Hello, this is Timer1 Callback! 

 Hello, this is Timer1 Callback! 
^C
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ ./mockinstall/usr/local/bin/main
./mockinstall/usr/local/bin/main: error while loading shared libraries: libgm_timer.so.0: cannot open shared object file: No such file or directory
ggm@ubuntu2004:~/tsmotter/software-timer (master)$ 
```

### Tests in bitbake context
- I'm able to bitbake the recipe sucesfuly
- I can check that the installation process took place accordingly
    - Given the recipe `do_install`, it is just installing with cmake like this: `cmake --install ${B} --prefix=${D}`
```bash
ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ bitbake software-timer
Loading cache: 100% |##########################################################################################################################################################################################################| Time: 0:00:00
Loaded 1730 entries from dependency cache.
NOTE: Resolving any missing task queue dependencies

Build Configuration:
BB_VERSION           = "2.0.0"
BUILD_SYS            = "x86_64-linux"
NATIVELSBSTRING      = "ubuntu-20.04"
TARGET_SYS           = "arm-oe-linux-gnueabi"
MACHINE              = "dogbonedark"
DISTRO               = "kiss"
DISTRO_VERSION       = "1.0"
TUNE_FEATURES        = "arm armv7a vfp thumb neon callconvention-hard"
TARGET_FPU           = "hard"
meta-arm
meta-arm-toolchain   = "kirkstone:bf98ef902e6e7042e46a69fb2df6c68d00de2764"
meta-kiss            = "main:da75f2090da8e147e2b9efa202c6aacae622a34d"
meta-motter          = "master:8e8f1bb01f34896a9e50c8062f111e0ec4bfec1a"
meta                 = "kirkstone:f09fca692f96c9c428e89c5ef53fbcb92ac0c9bf"

Initialising tasks: 100% |#####################################################################################################################################################################################################| Time: 0:00:00
Sstate summary: Wanted 7 Local 0 Mirrors 0 Missed 7 Current 131 (0% match, 94% complete)
NOTE: Executing Tasks
NOTE: Tasks Summary: Attempted 567 tasks of which 551 didn't need to be rerun and all succeeded.
ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ tree tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+a6ab5d489f-r0/packages-split/software-timer
tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+a6ab5d489f-r0/packages-split/software-timer
├── bin
│   └── main
└── lib
    ├── libgm_timer.so.0 -> libgm_timer.so.0.1
    └── libgm_timer.so.0.1

2 directories, 3 files
ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ objdump -x tmp-glibc/work/armv7at2hf-neon-oe-linux-gnueabi/software-timer/from-gitAUTOINC+a6ab5d489f-r0/packages-split/software-timer/bin/main | grep PATH
ggm@ubuntu2004:~/embedded-linux/sublime-platform/build(master)$ echo $?
1
```

### Tests on the target
- It is possible to see that the both: the application and the shared library are present on the rootfs and that they can be executed
```bash
root@dogbonedark:~# which main
/bin/main
root@dogbonedark:~# ls /lib/libgm_timer.so.0
/lib/libgm_timer.so.0
root@dogbonedark:~# main

 Hello, this is Timer1 Callback!

 Hello, this is Timer1 Callback!

 Hello, this is Timer1 Callback!

 Hello, this is Timer1 Callback!

 Hello, this is Timer2 Callback!

 Hello, this is Timer1 Callback!
^C
```