# cross3d.migrate is being used to centeralize any modules and code that will 
# be removed from cross3d, but will take more time to refactor ourt of cross3d.


# TODO: Find and remove these blurdev imports


# This PyQt4 signal is used to notify modules that they are about to be cleared.
# This means that their paths will be removed from sys.path and any modules
# for those paths will be removed from sys.modules.
import blurdev
aboutToClearPaths = blurdev.core.aboutToClearPaths

# blurdev.osystem is a module that provides operating system dependent functions.
# cross3d mostly uses it to simplify reading from the windows registry.
from blurdev import osystem

# dsofile is used to read and write custom UserProperties on studiomax files.
# It is also supported in the abstract software specific module so it can be
# used outside of studiomax.
from blurdev.media import dsofile

# These methods are used to parse filenames and look for Image Sequences.
from blurdev.media import imageSequenceFromFileName, imageSequenceInfo, imageSequenceRepr

# This is a library used to parse XML files.
from blurdev.XML.xmldocument import XMLDocument, XMLElement

# This is used by Studiomax's rescaletime module. It basicly provides a QMainWindow
# that is parented to 3ds Max to tell the user to not do anything while its processing.
# rescaletime is basicly a hack that allows us to change the frameRate of a max scene
# and preserve the key frame locations. It uses win32 to interact with the max interface.
from blurdev.gui import Window


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
