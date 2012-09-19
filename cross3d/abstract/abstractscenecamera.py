##
#	\namespace	blur3d.api.abstract.abstractsceneobject
#
"""
The AbstractSceneObject class provides the base foundation for the 3d 
Object framework for the blur3d system.  This class will provide a 
generic overview structure for all manipulations of 3d objects.

"""


from blur3d	import abstractmethod
from blur3d.api import SceneObject
from blur3d.constants import ObjectType
from blur3d import api


class AbstractSceneCamera(SceneObject):
	_objectType = ObjectType.Camera

	@abstractmethod
	def cameraType(self):
		"""Return the camera type for this camera instance
		
		:return: :data:`blur3d.constants.CameraType`
		
		"""
		return 0

	def isCameraType(self, cameraType):
		"""
		Return whether or not this camera is a kind of the inputed 
		camera type
		
		:param cameraType: :data:`blur3d.constants.CameraType`
		:rtype: bool

		"""
		return (self.cameraType() & cameraType) > 0

	@abstractmethod
	def lens(self):
		return 0.0

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
	def generateDotXSI(self, path, range=None):
		"""This is a temporary place for that method as it will belong to 
		blur3d.pipeline. 

		"""
		return False

	@abstractmethod
	def pictureRatio(self):
		"""Gets the camera's picture ratio.
		
		:rtype: float
			
		"""
		return 0.0

	@abstractmethod
	def setPictureRatio(self, pictureRatio):
		"""Sets the camera's picture ratio.
		
		:param distance: picture ratio
		:type distance: float
		:return: True if successful
		
		"""
		return False

	@abstractmethod
	def farClippingPlane(self):
		"""Gets the camera's far clipping plane distance.
		
		:rtype: float
		
		"""
		return 0

	@abstractmethod
	def setFarClippingPlane(self, distance):
		"""Sets the camera's far clipping plane distance.
		
		:type distance: float
		:return: True if successful
		
		"""
		return False

	@abstractmethod
	def nearClippingPlane(self):
		"""Gets the camera's near clipping plane distance.
		
		:rtype: float
			
		"""
		return 0

	@abstractmethod
	def setNearClippingPlane(self, distance):
		"""Sets the camera's near clipping plane distance.
		
		:param distance: picture ratio
		:type distance: float
		:return: True if successful

		"""
		return False


# register the symbol
api.registerSymbol('SceneCamera', AbstractSceneCamera, ifNotFound=True)

