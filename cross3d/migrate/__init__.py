# cross3d.migrate is being used to centeralize any modules and code that will 
# be removed from cross3d, but will take more time to refactor ourt of cross3d.

# All of the python modules in this folder are likely to be removed once the
# code that is dependent on it is refactored


# TODO: Find and remove these blurdev imports


# This Qt signal is used to notify modules that they are about to be cleared.
# This means that their paths will be removed from sys.path and any modules
# for those paths will be removed from sys.modules.
try:
	import blurdev
	aboutToClearPaths = blurdev.core.aboutToClearPaths
except ImportError:
	aboutToClearPaths = None

# This is used by Studiomax's rescaletime module. It basicly provides a QMainWindow
# that is parented to 3ds Max to tell the user to not do anything while its processing.
# rescaletime is basicly a hack that allows us to change the frameRate of a max scene
# and preserve the key frame locations. It uses win32 to interact with the max interface.
try:
	from blurdev.gui import Window
except ImportError:
	Window = None


#--------------------------------------------------------------------------------
# These methods were marked as @pendingdeprecation. They have been removed from
# cross3d, but code outside of cross3d may still attempt to use these functions.
# We need to search the code base to make sure those calls are removed.

"""
SceneCamera.isVrayCam()
Scene._nativeCameras()
Scene._nativeModels()
Scene._nativeRefresh()

Scene.application()
Scene.cameras()
Scene.models()
Scene.exportModel()
Scene.update()
ValueRange.multiply()
FrameRange.offset(...)
FrameRange.merge(...)
SceneModel.addAnimationClip(...)
Timecode.fromSeconds(...)
Timecode.toFrames()
FileSequence.sequenceForPath(...)
FileSequence.paddingCode()
FileSequence.codeName()
FileSequence.codePath()
SceneWrapper.setName(...)
SceneViewport.restoreState()
SceneViewport.storeState()
SceneAnimationController.controllerType()
Container.isVisible()
Container.setVisible(...)
"""
