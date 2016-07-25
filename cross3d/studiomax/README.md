# cross3d.studiomax
## Required Modules
These modules are used by the DCC implementation for Studiomax. You may need some or all of them.
### Py3dsMax:
Currently all maxscript code is using the blur studio's Py3dsMax module. If 3ds max's native python interface becomes a suitable replacement it will probably replace Py3dsMax. You can download the Py3dsMax dlx from https://github.com/blurstudio/Py3dsMax/releases. Currently you will need to add a startup maxscript similar to this code:
```maxscript
-- Check if the Python DLL is installed
if ( pymax != undefined ) then (
	-- Starting with Max 2015 we need to initialize Autodesk's python before our python is initialized
	if (python != undefined) and (finditem (getPropNames python) #exec == 0) do
		python.init()
	-- pymax did not have a init method in the past.
	if (finditem (getPropNames pymax) #init != 0) do
		pymax.init()
)
```
We name this startup script "scripts\Startup\1_init_python.ms" to make sure it is one of the first scripts run.

Alternately if you download and run this installer https://sourceforge.net/projects/blur-dev/ you should be able to find the Py3dsMax installer "C:\blur\installers\[datestamp]". Make sure the correct version of 3ds Max is checked in the installer. You can run the installer "Blur3dsMax${MAX_YEAR}_python${PYTHON_VERSION}_install_${MUI_SVNREV}_64.exe" to install Py3dsMax. Only Py3dsMax is required.

### pywin32
Some pywin32 modules are needed.
