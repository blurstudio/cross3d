##
#	\namespace	cross3d.studiomax.abstractsceneviewport
#
#	\remarks	The AbstractSceneRenderPass class will define all the operations for viewport interaction  
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		04/11/10
#

from Qt.QtCore import QObject

import cross3d
from cross3d import abstractmethod


class AbstractSceneViewport(QObject):
	"""
	The SceneRenderPass class will define all the operations for 
	viewport interaction  
	"""

	def __init__(self, scene, viewportID=0):
		super(AbstractSceneViewport, self).__init__()

		self._scene = scene
		self.name = ''
		self._viewOptions = {}
		self._slateIsActive = False
		self._slateText = ''
		self._nativePointer = None

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _nativeCamera(self):
		"""
			\remarks	return the viewport's native camera. added by douglas
			\return		<variant> camera | None
		"""
		return None

	def _setNativeCamera(self, nativeCamera):
		"""
			\remarks	sets the native camera of the current viewport. added by douglas
			\param		nativeCamera <variant> | <str>
			\return		<bool> success
		"""
		return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
		
	@abstractmethod
	def cameraName(self):
		"""Return the viewport's camera name

		"""
		return ''

	@abstractmethod
	def createCamera(self, name='Camera', type='Standard'):
		"""
			Creates a camera that matches that viewport.
		"""
		return None

	@abstractmethod
	def generateSnapshot(self, fileName, **options):
		"""
			Generates an image from the viewport in the specific path.
			:param filename: path to file
		"""
		return False

	@abstractmethod
	def generatePlayblast(self, fileName, **options):
		"""Generates a playblast in the specific path
		
		:param filename: path to file
		:param frameRange: two-item list of frames ie. (start, end)
		:param resolution: a :class:`Qt.QtCore.QSize` object

		"""
		return False

	@abstractmethod
	def setHeadlightIsActive(self, active):
		"""Sets the headlight of the camera of the viewport

		"""
		return False

	@abstractmethod
	def headlightIsActive(self):
		"""Returns if the status of the headlight

		"""
		return False

	@abstractmethod
	def size(self):
		"""Returns the viewport size
		
		:returns: two-item tuple of ints. ie. (width, height)

		"""
		return (0, 0)

	@abstractmethod
	def safeFrameSize(self):
		"""Returns the size of the safe frame. added by douglas
		
		:returns: two-item tuple of ints. ie. (width, height)
		
		"""
		return (0, 0)

	@abstractmethod
	def safeFrameIsActive(self):
		"""Returns the active of the safe frame. added by douglas

		"""
		return False

	@abstractmethod
	def setSafeFrameIsActive(self, active):
		"""Sets the active of the safe frame. added by douglas

		"""
		return False

	@abstractmethod
	def refresh(self):
		return False

	@abstractmethod
	def slateIsActive(self):
		return False

	@abstractmethod
	def setSlateIsActive(self, active):
		return False

	@abstractmethod
	def setSlateText(self, text=''):
		return False

	@abstractmethod
	def slateDraw(self):
		return False
		
	@abstractmethod
	def viewOptions(self):
		return {}
	
	@abstractmethod
	def setViewOptions(self, viewOptions):
		return False

	def nativePointer(self):
		return self._nativePointer
		
	def restoreViewOptions(self):
		return self.setViewOptions(self._viewOptions)
		
	def storeViewOptions(self):
		self._viewOptions = self.viewOptions()
		return True

	def camera(self):
		"""Return the viewport's camera
		
		:return: :class:`cross3d.SceneCamera`
		
		"""
		from cross3d import SceneCamera
		camera = self._nativeCamera()
		if camera:
			return SceneCamera(self._scene, camera)
		from cross3d.abstract.abstractscenecamera import AbstractSceneCamera
		return None

	def setCamera(self, camera):
		"""Sets the camera of the current viewport
		
		:param camera: :class:`cross3d.SceneCamera` or None

		"""
		if type(camera) == str or type(camera) == unicode:
			cam = camera
		elif camera:
			cam = camera.nativePointer()
		else:
			cam = None
		return self._setNativeCamera(cam)


# register the symbol
cross3d.registerSymbol('SceneViewport', AbstractSceneViewport)
