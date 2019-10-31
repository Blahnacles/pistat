################################################
## PiStat setup file
## SIMON LAFFAN
## MAY 2019
## Last edit - 07/05/2019
################################################
# Shell script to be run as part of installation
# Requires superuser permissions
# Safe to run multiple times - for debugging etc
################################################
# Get python 3.6
sudo $0
sudo apt-get update
sudo apt-install python3.6
# testing will happen with 3.6
echo Installing libraries for piStat:
echo Installing python libraries
sudo pip3 install numpy
sudo pip3 install pyqt5
sudo pip3 install pyusb
sudo pip3 install scipy
sudo pip3 install gps
sudo pip3 install gpsd-py3
sudo pip3 install pandas
mv piStat.sh ~/Desktop