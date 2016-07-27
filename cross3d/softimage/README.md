# cross3d.softimage
Due to how blur has softimage setup I am unchecking the "Use Python Installed with Softimage(Windows Only)" checkbox. To access this click on the File menu -> select Preferences... Select Scripting from the list of prefs on the left. This may not be necessary if you install the required python modules inside Softimage.
## Required Modules
These modules are used by the DCC implementation for Softimage. You may need some or all of them.
### PySoftimage
PySoftimage is a python module used to expose the softimage api to python.
Ultimately all it is doing is providing a easy interface for the win32com.client.Dispatch calls. Ideally we will remove the need for this module.

To install this module, copy the PySoftimage folder from cross3d\softimage\_PySoftimage_setup to a valid site-packages folder.
### PyQt4
You should be able use the standard PyQt4 installers available from Riverbank. https://www.riverbankcomputing.com/software/pyqt/download.

At Blur, we currently install msvc2008 Qt in a global location and PyQt4 inside python's site-packages.
### win32com
PySoftimage and other functionality use pywin32 to control Softimage.
### pywintypes
Used to capture exceptions raised by Softimage.
### win32clipboard
Used to place text into the clipboard. Can be replaced by Qt.

### Example from Softimage Script Editor

```python
from PySoftimage import xsiPrint
import cross3d
xsiPrint(cross3d.Scene)
s = cross3d.Scene()
for o in s.objects():
	xsiPrint(o)
```
