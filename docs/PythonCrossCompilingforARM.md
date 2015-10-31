The tutorial tells how to cross-compile Python2.7.3 for ARM.
Before you start, you need to download Python-2.7.3 source file and Python-2.7.3-xcompile.patch.

1. Decompress Python-2.7.3 source file and **cd** to the source directory.
2. ./configure
3. make python Parser/pgen
4. mv python hostpython
5. mv Parser/pgen Parser/hostpgen
6. make distclean
7. patch -p1 < ./Python-2.7.3-xcompile.patch 
8. Cross-compile the **zlib** library and place the compiled files in **/python**
8.  ./configure --host=arm-xilinx-linux-gnueabi --prefix=/python CC=arm-xilinx-linux-gnueabi-gcc   CXX=arm-xilinx-linux-gnueabi-g++   AR=arm-xilinx-linux-gnueabi-ar   RANLIB=arm-xilinx-linux-gnueabi-ranlib     
9. modify the file /Modules/Setup: Uncomment the lile containing zlib and cpickle, because we need these two modules in OFTest.
10. make HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen BLDSHARED="arm-xilinx-linux-gnueabi-gcc -shared" CROSS_COMPILE=arm-xilinx-linux-gnueabi- CROSS_COMPILE_TARGET=yes HOSTARCH=arm-linux BUILDARCH=x86_64-linux-gnu  
11.   make install HOSTPYTHON=./hostpython BLDSHARED="arm-xilinx-linux-gnueabi-gcc -shared" CROSS_COMPILE=arm-xilinx-linux-gnueabi- CROSS_COMPILE_TARGET=yes prefix=/home/ubuntu/Python-2.7.3/python_arm
12. The compled python files are in **/home/ubuntu/Python-2.7.3/python_arm**
13. Install  **scapy** python library 

