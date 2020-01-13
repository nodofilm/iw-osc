# iw-osc
Inertia Wheels to OSC Desktop App

### About
This simple open-source desktop application reads the Inertia Wheels API from the Receiver via USB and transmits Pan/Tilt/Roll and Focus/Iris/Zoom data via OSC (Open Sound Control) to the desired IP address and Port. 

The secondary purpose of this application is to provide a proof of concept and example code for a desktop application that receives and interprets the Inertia Wheels API. 

### Virtual Production
Because OSC is an open standard, there are many cross-platform plug-in's that enable the Inertia Wheels to interface with various virtual production environments. We have compiled some popular plugins:

|Platform|Plugin|
|--------|------|
|Cinema4D|[GripTools](https://www.griptools.io/io_osc.php)|
|Unreal Engine|[UE4-OSC](https://github.com/monsieurgustav/UE4-OSC)|
|Unity|[UnityOSC](https://github.com/thomasfredericks/UnityOSC)|

### GUI


### Releases


## Development

### Dependecies
In development, we use PyCharm and create a virtual environment using Python 3.7 and the following:

|Package|Version|
|-------|-------|
|PyQt5  |5.14.1|
|PyQt5-sip|12.7.0|
|pyserial|3.4|
|python-osc|1.7.4|
|setuptools|40.8.0|

### Build Instructions

To build, we use PyInstaller 3.5

#### Mac
1. Open Terminal
2. `cd` into the folder with main.py
3. Run `pyinstaller --onefile --windowed -i 'icon.icns' --osx-bundle-identifier 'com.nodo.iwosc' --name 'IW-OSC' main.py`
4. To make the app retina compatible:
    1. In the newly-created IW-OSC.spec file, add `,info_plist={'NSHighResolutionCapable': 'True'` after `bundle_identifier='com.nodo.iwosc'`
    2. Re-compile with the spec file using: `pyinstaller --onefile --windowed IW-OSC.spec main.py`

  
#### Windows
1. Open Command Prompt
2. `cd` into the folder with main.py
3. Run `pyinstaller.exe -w --clean main.py`
