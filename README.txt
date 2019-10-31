Installation Guide
The following guide will assume the hardware has been assembled on a Raspberry Pi unit running Raspbian, a flavour of Debian distributed by the Raspberry Pi Foundation. Raspbian images may be downloaded by following the directions here: https://www.raspberrypi.org/downloads/raspbian/
It is recommended that users unfamiliar with linux and OS images follow the NOOBS guide here: https://www.raspberrypi.org/downloads/noobs/

Raspbian comes with python 3 preinstalled, as well as some useful libraries such as tKinter. Once installation is successful, follow the steps below:

1. Download the pistat repository from bitbucket.

2. Run the pistatInstall.sh script as SUPERUSER
	Via terminal: 	cd /your_install_location/pistat
			sudo pistatInstall.sh

3. Once the installation has completed, run the gui as SUPERUSER via python 3.1 or greater to launch the app
	Via terminal: sudo python3 gui.py

Optional: Add a desktop icon – move the piStat.sh file to the desktop, and complete the 	following steps:
	3a. open terminal, and run the following commands:
	cd /home/pi/Desktop
	sudo chmod +x piStat.sh
