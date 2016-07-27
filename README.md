# Cross3d
A python implementation of commands that work in multiple programs(Studiomax, Softimage).
It utilizes a abstract definition of commands, and a software specific implementation of those commands.

# Package Overview
## cross3d
The majority of classes used by scripters in cross3d are directly inside the cross3d module. 
### cross3d.Scene
Used to access information about the current scene. Create as many instances of this class as needed.
### cross3d.application
Used to access information about the current application(application name, version, etc). Instance of `cross3d.Application`. Do not manually create a new instance of cross3d.Application.
### cross3d.dispatch
Used to monitor the DCC for callbacks. It automatically connects/disconnects to the DCCs callback mechanism so if a callback is not used it will not cause extra overhead(depending on the DCC). Instance of `cross3d.Dispatch`. Do not manually create a new instance of cross3d.Dispatch.
### cross3d.constants
This class contains enumerators used in cross3d. Instead of passing string objects as identifiers to functions these enumerators are passed.
### cross3d.external
This class is used to lookup install paths for and to run scripts in DCCs regardless of what DCC or lack of a DCC python is currently running in.
## cross3d.migrate
This module is being used to migrate blur pipeline specific functionality from our pipeline. Most of the contents of this module will probably be removed.
## cross3d.classes
This module contains classes that do not need software specific overrides. You should not directly use these classes. The classes that are used by scripters will be available directly from cross3d. `cross3d.FileSequence` for example.
## DCC Specific implementations
These modules are the core of how cross3d works. cross3d.abstract is defines how scripters work with the api and all DCC specific implementations must subclass from inside abstract.
## cross3d.abstract
This module defines the generic structure of the cross3d classes. All software specific implementations inherit from classes in this module. If cross3d is imported in a standard python interpreter(outside of a DCC) these modules should import without error. If a one of these classes is not defined for a specific DCC the class defined inside this module will be used.
At the bottom of most of the python files inside this folder you will see code similar to this:
```python
# register the symbol
cross3d.registerSymbol('Scene', AbstractScene, ifNotFound=True)
```
This code is used to store the AbstractScene class(`cross3d.abstract.abstractscene.AbstractScene`) in the official cross3d name of `cross3d.Scene`. 'ifNotFound=True'  should only be used in the abstract module. It tells registerSymbol to only register this class if a subclass hasn't already registered for that class.
## cross3d.maya, cross3d.motionbuilder, cross3d.studiomax, etc
These modules subclass from cross3d.abstract. Not everything in cross3d.abstract needs to be implemented for cross3d to function in a DCC. Any changes to public methods must be reflected in all of these modules and cross3d.abstract to maintain the cross DCC integration.

At the bottom of most of the python files inside this folder you will see code similar to this:
```python
# register the symbol
cross3d.registerSymbol('Scene', StudiomaxScene)
```
This code is used to store the StudiomaxScene class(`cross3d.studiomax.studiomaxscene.StudiomaxScene`) in the official cross3d name of `cross3d.Scene`.

# Additional packages
* Currently `PyQt4` is required for cross3d.
* `cross3d.FCurve` requires `numpy`

Depending on the DCC some additional modules are needed. These are documented in the DCC's readme.md file.
cross3d.FileSequence has a few methods that use ffmpeg. Currently you can pass the path to ffmpeg as a argument to these functions. By default it assumes that ffmpeg is in the path variable.
# Examples
Get objects in a scene:
```python
from cross3d import Scene
scene = Scene()
for obj in scene.objects():
	print obj
```
output(when run inside 3ds max):
```python
<StudiomaxSceneObject (Box001)>
<StudiomaxSceneObject (Box002)>
<StudiomaxSceneObject (Sphere001)>
<StudiomaxSceneObject (Sphere002)>
<StudiomaxSceneCamera (Camera001)>
```
To get a list of camera's in the scene:
```python
from cross3d import Scene
from cross3d.constants import ObjectType
scene = Scene()
for obj in scene.objects(type=ObjectType.Camera):
	print obj
```
output(when run inside 3ds max):
```python
<StudiomaxSceneCamera (Camera001)>
```

```python
>>> sel = scene.selection()[0] # Get the first selected object
>>> sel.objectType() == ObjectType.Geometry # Check the type of the selection
True
>>> print 'fps:', scene.animationFPS(), 'Frame Range:', scene.animationRange()
fps: 30.0 Frame Range: cross3d.FrameRange( 0, 100 )
>>> scene.currentFileName()
C:\Max2016_x64\3ds Max 2016\scenes\cross3d.max
>>> from blur3d.constants import CameraType
>>> camera = Scene.createCamera(scene, 'TestCamera', constants.CameraType.Physical)
>>> camera
<StudiomaxSceneCamera (TestCamera)>
```
### cross3d.external
The cross3d.external class allows you to get the installed path for supported DCCs from within any dcc or even outside of a dcc.
```python
>>> import cross3d
>>> cross3d.external('Maya').binariesPath()
C:\Program Files\Autodesk\Maya2016\bin
>>> cross3d.external('Maya').binariesPath(2014)
C:\Program Files\Autodesk\Maya2014\bin
>>> cross3d.external('StudioMax').binariesPath(2012)
C:\Max2012_x64\3ds Max 2012
>>> cross3d.external('StudioMax').binariesPath(2013) # StudioMax 2013 is not installed on this computer
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "c:\blur\dev\local\code\python\lib\cross3d\studiomax\external.py", line 136, in binariesPath
    raise Exceptions.SoftwareNotInstalled('Studiomax', version=dispVersion, architecture=architecture, language=language)
cross3d.classes.exceptions.SoftwareNotInstalled: Studiomax  2013 64-bit not installed for English.
```
Start 3ds Max(with interface) and run script(valid filename or text of script)
```python
cross3d.external('StudioMax').runScript(script, 2016, headless=False) 
```

## Environment Variables
cross3d uses environment variables to configure specific settings for module initialization.

### CROSS3D_LOGGING_LEVEL
Setup logging for the cross3d library. To access the logger object call cross3d.logger. If the environment variable 
"CROSS3D_LOGGING_LEVEL" is set a StreamHandler will be created that prints all output to sys.stdout. Otherwise it will create a NullHandler.

### CROSS3D_DEBUG_LEVEL
This allows developers to create additional workflows inside the code that helps with debugging and development. By default it defaults to DebugLevels.Disabled, but you can control the default with the "CROSS3D_DEBUG_LEVEL" environment variable.
To change the current debug level: `cross3d.debugLevel = cross3d.constants.DebugLevels.Mid`
To check if the current debug level is Mid or higher: `cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid`

### CROSS3D_ABSTRACTMETHOD_MODE
Similar to CROSS3D_DEBUG_LEVEL, this variable allows a cross3d developer to have a log message sent any time a abstractmethod function is called and is not overriden by the DCC specific code. This is useful for auditing what functions still need implemented. 

Here are the valid values:
* "": A empty string disables any logs or exceptions from being raised. The Default.
* "raise": If a abstractmethod is called without a subclass, raise a exception.
* "warn": If a abstractmethod is called log a message that it was called.

### CROSS3D_DEBUG_MODULE
By default cross3d suppresses exceptions when it imports the software specific module. It uses the first module that successfully imports. When programming a software specific module this makes it hard to debug. If you set the environment variable CROSS3D_DEBUG_MODULE to the name of the module you are working on it will only try to load that module(and abstract) and it will raise all exceptions.

### CROSS3D_STUDIO_IGNORED_[DCCNAME]
Currently: CROSS3D_STUDIO_IGNORED_MAYA, CROSS3D_STUDIO_IGNORED_MOTIONBUILDER, CROSS3D_STUDIO_IGNORED_SOFTIMAGE, CROSS3D_STUDIO_IGNORED_STUDIOMAX

These variables are used to ignore speciffic versions of DCC when using cross3d.external. Each of these variables should contain a comma seperated list of versions that if installed should be ignored when automatically choosing the version of the DCC. It is ignored if the version is explicitly requested.

# History
cross3d was originally called blurapi. Eric Hulser and a few others wrote the initial framework in late 2008. It was later renamed blur3d with a major refactor. blur3d has been used in many tools at blur. It has been touched by most of the TD's and programmers at blur at some point. When releasing it as a module on github we renamed it to cross3d and removed(planning to remove) a lot of the blur specific logic to reduce the number of requirements.

## TODO:
blur3d has been used in blur for several years. It uses several blur specific api's and is dependent on several of blur api's that are not currently easily available via open source, and in most cases are completely unnecessary outside of blur. We are migrating blur3d to cross3d we are taking the opportunity to remove the extra dependencies. Here are a list of upcoming changes planned to make cross3d easier to integrate in other pipelines.

* **PyQt4:** Currently cross3d is dependent on PyQt4 which is not easily available in most DCCs. We need it for our database api, so we end up compiling a compatible version for each DCC. If possible we will remove Qt dependencies entirely(I think `cross3d.dispatch` is the only module that currently needs Qt for signals). Otherwise I will make it so cross3d can be configured to use PyQt4 or PySide.
* **cross3d.enum.enum:** Currently many of the enums are using `cross3d.enum.enum`. These should all be converted to EnumGroup subclasses. I want to verify how each is being used and make sure the conversion doesn't cause problems.
* **cross3d.migrate:** This module contains duplicate code for modules that are need for cross3d to function. Some of them may end up in separate packages and some may be removed entirely.
  * **XML:** This module may be removed, or replaced with a more standard xml parsing module.
  * **dsofile:** This module is used to parse custom file properties in max files. It will probably not be removed. To be used it requires downloading a dll. See module docstring for more info.
  * **imagesequence:** This is a collection of functions used to parse a filename for frame numbers and get a list of filenames or representation of a image sequence on disk. It is used by `cross3d.FileSequence` and will probably be moved into that module.
  * **winregistry:** Several convenience methods used to pull info from the windows registry. These functions are used by the external modules to find the install location of DCCs. It will most likely stay in cross3d.
* **Cross platform support:** Currently at blur all of our 3d DCC's are running on windows. While nothing in cross3d requires windows, it has not been tested on other platforms so additional development will be needed for it to work on Linux or Mac. `cross3d.external` for example currently uses winregistry to find the installed location of the requested DCC. Softimage uses pywin32 for just about everything.
