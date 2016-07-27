# cross3d.studiomax
## Required Modules
These modules are used by the DCC implementation for Studiomax. You may need some or all of them.
### PyQt4:
While you can use the vanilla PyQt4 source code, for it to work inside 3ds Max you need to compile it with the correct version of Visual Studio. Currently if you can't compile it yourself, you can extract the the Qt and PyQt4 installers from the BlurOffline installer at https://sourceforge.net/projects/blur-dev/. See alternate download method of Py3dsMax.

At Blur, we currently install msvc2008 Qt in a global location and PyQt4 inside python's site-packages. For Max 2016 we install msvc2012 Qt inside [MaxRoot] and PyQt4 inside [MaxRoot]\python\Lib.
### Py3dsMax:
Currently all maxscript code is using the blur studio's Py3dsMax module. If 3ds max's native python interface becomes a suitable replacement it will probably replace Py3dsMax. You can download the Py3dsMax dlx from https://github.com/blurstudio/Py3dsMax/releases.
cross3d\studiomax\_Py3dsMax_setup contains a example of how to setup Py3dsMax and use the standard 64bit python's site-packages.

1. Copy 1_init_pyhelper.ms and 2_init_python.ms to [MaxRoot]\scripts\Startup.
2. Copy the scripts inside site-packages to [MaxRoot]\python\Lib\site-packages

Alternately if you download and run this installer https://sourceforge.net/projects/blur-dev/ you should be able to find the Py3dsMax installer "C:\blur\installers\[datestamp]". Make sure the correct version of 3ds Max is checked in the installer. You can run the installer "Blur3dsMax${MAX_YEAR}_python${PYTHON_VERSION}_install_${MUI_SVNREV}_64.exe" to install Py3dsMax. Only Py3dsMax is required.

### pywin32
Some pywin32 modules are needed. These need to be in sys.path. See cross3d\studiomax\_py3dsMax_setup\py3dsMax_setup.py for a example.

# Example from the MAXscript Listener
Note: The -- denotes the output of the command run on the line above.
```maxscript
cross3d = pymax.import "cross3d"
--<module 'cross3d' from 'C:\Python27\Lib\site-packages\cross3d\__init__.pyc'>
s = cross3d.Scene()
--<cross3d.studiomax.studiomaxscene.StudiomaxScene object at 0x000000005A322048>
s.objects()
--#($Sphere:Sphere001 @ [-33.898304,-0.000001,14.237288], $Sphere:Sphere002 @ [-138.305084,0.000001,-11.525424])
```
