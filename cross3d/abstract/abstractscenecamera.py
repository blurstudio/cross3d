##
#	\namespace	blur3d.api.abstract.abstractscenecamera
#
#	\remarks	The AbstractSceneObject class provides the base foundation for the 3d Object framework for the blur3d system
#				This class will provide a generic overview structure for all manipulations of 3d objects
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blur3d	import abstractmethod
from blur3d.api import SceneObject
from blur3d.constants import ObjectType
from blur3d import api

class AbstractSceneCamera(SceneObject):
	"""
		The AbstractSceneObject class provides the base foundation for the 3d 
		Object framework for the blur3d system.  This class will provide a 
		generic overview structure for all manipulations of 3d objects.

	"""

	_objectType = ObjectType.Camera

	def __init__(self, scene, nativeCamera, target=None):
		super(AbstractSceneCamera, self).__init__(scene, nativeCamera)
		self._viewOptions = {}
		self._target = target

	def target(self):
		return self._target

	def interest(self):
		return None

	def setInterest(self, interest):
		pass

	def isCameraType(self, cameraType):
		"""
			Return whether or not this camera is a kind of the inputed camera type. Expecting blur3d.constants.CameraType. 
		"""
		return (self.cameraType() & cameraType) > 0
	
	def originalFilmWidth(self, storeWidth=False):
		""" Returns the original Film width stored in userProps as 'overscanOrigFilmWidth'. If this is not
		set it returns the cameras current filmWidth.
		:param storeWidth: If the original width is not stored in userProps, store it before returning. Defaults to False
		"""
		originalFilmGate = self.userProps().get('overscanOrigFilmWidth')
		if originalFilmGate == None:
			originalFilmGate = self.filmWidth()
			if storeWidth:
				self.setOriginalFilmWidth(originalFilmGate)
		return originalFilmGate

	def setOriginalFilmWidth(self, width):
		""" Store the film width on the cameras userProps as 'overscanOrigFilmWidth'.
		:param width: the film width to store as the original value
		"""
		self.userProps()['overscanOrigFilmWidth'] = width

	def overscan(self, stored=True):
		""" Returns the current overscan value of the camera.
		:param stored: If false calculates the current overscan instead of returning the stored value. This is not the default 
					because the stored value is truncated so the value can not be guaranteed. Defaults to True
		"""
		if stored:
			ret = self.userProps().get('overscanValue')
			if ret != None:
				return ret
		return ((self.filmWidth()/self.originalFilmWidth()) - 1) * 100.0

	def setOverscan(self, overscan):
		""" Stores the overscan value in the cameras userProps as 'overscanValue' and adjusts the camera's
		filmWidth.
		:param overscan: The ammount of overscan applied to the cameras film width
		"""
		self.userProps()['overscanValue'] = overscan
		self.setFilmWidth(self.originalFilmWidth(storeWidth=True) * (1.0 + (overscan / 100.0)))

	def overscanRenderSize(self, size=None, storeSize=False, overscan=None):
		""" Returns the render size for the camera's overscan value. Uses self.originalRenderSize if size is
		not provided.
		:param size: None or a two item array that is multiplied by the camera overscan. Defaults to None.
		:param storeSize: If the original render size is not stored in userProps, store it before returning it. Defaults to False.
		:param overscan: Override the camera overscan value.
		:return: [width, height] The overscan render size.
		..seealso:: modules `originalRenderSize`
		"""
		if overscan == None:
			overscan = self.overscan()
		mult = (1.0 + (overscan / 100.0))
		if size == None:
			size = self.originalRenderSize()
		if storeSize:
			self.setOriginalRenderSize(size)
		return [s * mult for s in size[:2]]

	def originalRenderSize(self, storeSize=False):
		""" Returns the pre-overscan render size stored on in the cameras userProps under 'overscanOrigRenderSize'.
		:param storeSize: If the user prop doesn't exist yet, call self.setOriginalRenderSize with the scene's current render size
		:returns: [width, height] The original render size of the scene.
		"""
		size = self.userProps().get('overscanOrigRenderSize')
		if size == None:
			size = self._scene.renderSize()
			size = (size.width(), size.height())
			if storeSize:
				self.setOriginalRenderSize(size)
		return size
	
	def setOriginalRenderSize(self, size):
		""" Store the render size used for calculating 
		"""
		self.userProps()['overscanOrigRenderSize'] = size

	@abstractmethod
	def animateTurntable(self, objects=[], startFrame=1, endFrame=100):
		"""
			Orbits the camera around the given object(s).
		"""
		pass

	@abstractmethod
	def cameraType(self):
		"""
			Returns the camera type for this camera instance as blur3d.constants.CameraType.
		"""
		return 0

	@abstractmethod
	def filmWidth(self):
		pass
	
	@abstractmethod
	def filmHeight(self):
		return None

	@abstractmethod
	def setFilmHeight(self, height):
		pass

	@abstractmethod
	def fov(self, rounded=False):
		return 0.0

	@abstractmethod
	def lens(self, filmWidth=None, rounded=False):
		return 0.0

	@abstractmethod
	def setFilmWidth(self, width):
		pass

	@abstractmethod
	def setLens(self, value):
		return False

	@abstractmethod
	def setShowsFrame(self, switch):
		return False

	@abstractmethod
	def showsFrame(self):
		return False

	@abstractmethod
	def setShowsCustomParameters(self, switch):
		return False

	@abstractmethod
	def setHeadlightIsActive(self, switch):
		return False

	@abstractmethod
	def headlightIsActive(self):
		return False

	@abstractmethod
	def hasMultiPassEffects(self):
		return False

	@abstractmethod
	def renderMultiPassEffects(self):
		return False

	@abstractmethod
	def pictureRatio(self):
		"""
			Gets the camera's picture ratio.
			:rtype: float
		"""
		return 0.0

	@abstractmethod
	def outputType(self):
		return ''

	@abstractmethod
	def setOutputType(self, outputType):
		return False

	@abstractmethod
	def exposureEnabled(self):
		return False

	@abstractmethod
	def setExposureEnabled(self, exposureEnabled):
		return False

	@abstractmethod
	def vignettingEnabled(self):
		return False

	@abstractmethod
	def setVignettingEnabled(self, vignettingEnabled):
		return False

	@abstractmethod
	def whiteBalance(self):
		return ''

	@abstractmethod
	def setWhiteBalance(self, whiteBalance):
		return False

	@abstractmethod
	def shutterAngle(self):
		return 0

	@abstractmethod
	def setShutterAngle(self, shutterAngle):
		return False

	@abstractmethod
	def shutterOffset(self):
		return 0

	@abstractmethod
	def setShutterOffset(self, shutterOffset):
		return False

	@abstractmethod
	def bladesEnabled(self):
		return 0

	@abstractmethod
	def setBladesEnabled(self, bladesEnabled):
		return False

	@abstractmethod
	def blades(self):
		return 0

	@abstractmethod
	def setBladed(self, blades):
		return False

	@abstractmethod
	def anisotropy(self):
		return 0

	@abstractmethod
	def setAnisotropy(self, anisotropy):
		return False

	@abstractmethod
	def distortionType(self):
		return ''

	@abstractmethod
	def setDistortionType(self, distortionType):
		return False

	@abstractmethod
	def distortion(self):
		return 0.0

	@abstractmethod
	def setDistortion(self, distortion):
		return False

	@abstractmethod
	def setPictureRatio(self, pictureRatio):
		"""
			Sets the camera's picture ratio.
			:param distance: picture ratio
			:type distance: float
			:return: True if successful
		"""
		return False

	@abstractmethod
	def farClippingPlane(self):
		"""
			Gets the camera's far clipping plane distance.
			:rtype: float
		"""
		return 0

	@abstractmethod
	def setFarClippingPlane(self, distance):
		"""
			Sets the camera's far clipping plane distance.
			:type distance: float
			:return: True if successful
		"""
		return False

	@abstractmethod
	def nearClippingPlane(self):
		"""
			Gets the camera's near clipping plane distance.
			:rtype: float
		"""
		return 0

	@abstractmethod
	def setNearClippingPlane(self, distance):
		"""
			Sets the camera's near clipping plane distance.
			:param distance: picture ratio
			:type distance: float
			:return: True if successful
		"""
		return False
	
	@abstractmethod
	def clippingEnabled(self):
		return False
	
	@abstractmethod
	def setClippingEnabled(self, state):
		return

	@abstractmethod
	def generateRender(self, **options):
		"""
			\remarks renders an image sequence form that camera with the current render settings
			\param path <String>
			\param frameRange <FrameRange>
			\param resolution <QtCore.QSize>
			\return <blur3d.api.constants.CameraType>
		"""
		return False

	@abstractmethod
	def viewOptions(self):
		return {}

	@abstractmethod
	def setViewOptions(self, viewOptions):
		return False
	
	@abstractmethod
	def isVrayCam(self):
		""" 
			Returns True if this is a vray camera, False otherwise. 
		"""
		return False

	def matchCamera(self, camera):
		"""
			Match this camera to another one.
		"""
		return False

	def restoreViewOptions(self):
		"""
			Stores this camera view options.
		"""
		return self.setViewOptions(self._viewOptions)

	def storeViewOptions(self):
		"""
			Restores previously stored view options.
		"""
		self._viewOptions = self.viewOptions()
		return True

# register the symbol
api.registerSymbol('SceneCamera', AbstractSceneCamera, ifNotFound=True)

