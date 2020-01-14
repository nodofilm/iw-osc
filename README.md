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

### Download Release Versions of App
|Release|Mac   | Windows|
|-------|------|-------|
|V1     |[Download](https://www.dropbox.com/s/yne1zlln40gbpbe/IW-OSC-V1.zip?dl=0)|Coming Soon...|

### GUI

This app comes with a simple GUI that allows you to control:

* Enable/Disable Pan/Tilt/Roll Channels
* Set the format of Pan/Tilt/Roll Data to:
    * Raw Integers - The Raw Encoder Data0
    * Cumulative Radians - The wheel data in radians that count rotations
    * Finite Radians - The wheel data in radians from -1.0f to 1.0f
* Enable/Disable Focus/Iris/Zoom Channels
* Set the format of Focus/Iris/Zoom
    * Raw Integers - From 0 to 32767
    * Float - From 0.0f to 1.0f
* Set OSC IP Address/Port
* Set Incoming UART Port

![GUI Example](https://images.squarespace-cdn.com/content/v1/5c9296ea70468017a9b29717/1578958714682-0D1P19JSQ6WK4JEAH76G/ke17ZwdGBToddI8pDm48kIfmEvYrxwLn8L2GdmCsAQFZw-zPPgdn4jUwVcJE1ZvWEtT5uBSRWt4vQZAgTJucoTqqXjS3CfNDSuuf31e0tVHCrK-xG8qM-tDqbIhh2zI3XieVLy7NcbluJ4JTdjCyRpu3E9Ef3XsXP1C_826c-iU/IW-OSC-Screen.png?format=500w)


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
