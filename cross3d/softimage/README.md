# cross3d.softimage
## Required Modules
These modules are used by the DCC implementation for Softimage. You may need some or all of them.
### PySoftimage
PySoftimage is a python module used to expose the softimage api to python.
### win32com
PySoftimage and other functionality use pywin32 to controll softimage.
### pywintypes
Used to capture exceptions raised by Softimage.
### win32clipboard
Used to place text into the clipboard. Can be replaced by Qt.
