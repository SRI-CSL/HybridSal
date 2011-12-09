#!/bin/sh

#
# This script is used to install hybridsal2xml
#

echo "Installing hybridsal2xml. Copyright (c) SRI International 2003."
echo "-------------------------------------------------------------------------"

check_prog ()
{
		if $1 > /dev/null 2> /dev/null ; then
				echo "program $2 was found..."
		else
				echo "Error: Failed to detect program $2"
				exit -1
		fi
}

# check_prog "sed --version" sed
# check_prog "chmod --version" chmod
check_prog "java -version" java

salenv_dir=`pwd`
antlrpath=$1
rtjarpath=$2
jikespath=$3

if [ -z $antlrpath ] ; then
	antlrpath=$salenv_dir
fi
if [ -z $rtjarpath ] ; then
	rtjarpath=$salenv_dir
fi
if [ -z $jikespath ] ; then
	jikespath=javac
fi

if [ ! -r $antlrpath/antlr.jar ] ; then
	echo "Antlr path not ok"
	echo "Usage: ./install.sh <ANTLR_PATH> <RTJAR_PATH> <JIKES_PATH>"
	exit -1
fi
if [ ! -f $rtjarpath ] ; then
	echo "rt.jar path not ok"
	echo "Usage: ./install.sh <ANTLR_PATH> <RTJAR_PATH> <JIKES_PATH>"
fi

echo "Installing hybridsal2xml. Copyright (c) SRI International 2003."
echo "-------------------------------------------------------------------"
echo "Installing hybridsal2xml at : $salenv_dir"

# ?? touch *.class
sed -e "s|__ANTLR_PATH__|$antlrpath|g;s|__JIKES_PATH__|$jikespath|g;s|__RTJAR_PATH__|$rtjarpath|g" Makefile.in > Makefile
make 
echo "hybridsal2xml installation complete.\n"

echo "Testing hybridsal2xml installation"
make test
echo "Testing complete."
echo "See README file for more details."

