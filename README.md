# iw-osc
Inertia Wheels to OSC Desktop App

### About
This simple desktop application reads the Inertia Wheels API from the Receiver via USB and transmits Pan/Tilt/Roll and Focus/Iris/Zoom data via OSC (Open Sound Control) to the desired IP address and Port. 

The secondary purpose of this application is to provide a proof of concept and example code for a desktop application that receives and interprets the Inertia Wheels API. 

### Releases


### Dependecies
In development, we use PyCharm and create a virtual environment using Python 3.4 and the following:

|Package|Version|
|-------|-------|
|PyQt5  |5.14.1|
|PyQt5-sip|12.7.0|
|pyserial|3.4|
|python-osc|1.7.4|
|setuptools|40.8.0|

To build, we use PyInstaller 3.5

### Build Instructions

#### Mac
1. Open Terminal
2. `cd` into the folder with main.py
3. Run `pyinstaller --onefile --windowed main-apple.spec main.py`
  
#### Windows
1. Open Command Prompt
2. `cd` into the folder with main.py
3. Run `pyinstaller.exe -w --clean --hidden-import=pyserial main-windows.spec main.py`
