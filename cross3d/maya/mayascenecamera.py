import maya.OpenMaya as om
import cross3d
import math
from cross3d.abstract.abstractscenecamera import AbstractSceneCamera
from cross3d.constants import RotationOrder

class MayaSceneCamera(AbstractSceneCamera):
	def clippingEnabled(self):
		# As far as I can tell, maya doesn't provide a way to disable the near/far clip planes
		# so store it as a user prop so we can diff against the camera files.
		return self.userProps().setdefault('clipping_enabled', False)
		
	def setClippingEnabled(self, state):
		# As far as I can tell, maya doesn't provide a way to disable the near/far clip planes
		# so store it as a user prop so we can diff against the camera files.
		self.userProps()['clipping_enabled'] = state

	@classmethod
	def defaultRotationOrder(cls):
		""" The default rotation order when creating new cameras.
		
		Returns:
			cross3d.constants.RotationOrder
		"""
		return RotationOrder.ZXY

	def farClippingPlane(self):
		return self._nativeTypePointer.farClippingPlane()

	def setFarClippingPlane(self, distance):
		self._nativeTypePointer.setFarClippingPlane(distance)
		return True

	def nearClippingPlane(self):
		return self._nativeTypePointer.nearClippingPlane()

	def setNearClippingPlane(self, distance):
		self._nativeTypePointer.setNearClippingPlane(distance)
		return True
	
	def filmWidth(self):
		""" Returns the film_width of the camera in mm.
			:return: film_width (float)
		"""
		# Maya uses inches, convert inches to mm. 1in / 25.4mm
		return self._nativeTypePointer.horizontalFilmAperture() * 25.4

	def setFilmWidth(self, width):
		""" Sets the film_width value for the camera.
			:param: width <float>
			:return: True
		"""
		# Maya uses inches, convert inches to mm. 1in / 25.4mm
		self._nativeTypePointer.setHorizontalFilmAperture(width / 25.4)
		return True

	def filmHeight(self):
		""" Returns the film_height of the camera in mm.
			:return: film_width (float)
		"""
		# Maya uses inches, convert inches to mm. 1in / 25.4mm
		return self._nativeTypePointer.verticalFilmAperture() * 25.4

	def setFilmHeight(self, height):
		""" Sets the film_height value for the camera.
			:param: width <float>
			:return: True
		"""
		# Maya uses inches, convert inches to mm. 1in / 25.4mm
		self._nativeTypePointer.setVerticalFilmAperture(height / 25.4)
		return True
	
	def fov(self, rounded=False):
		fov = math.degrees(self._nativeTypePointer.horizontalFieldOfView())
		if rounded:
			return int(round(fov))
		return fov
	
	def _nativeFocalLength(self):
		return self._nativeTypePointer.focalLength()
	
	def setLens(self, value):
		self._nativeTypePointer.setFocalLength(value)
	
	def matchViewport(self, viewport):
		return self.matchCamera(viewport.camera())

	def matchCamera(self, camera):
		""" Match this camera to another one. """
		self.setParameters(camera.parameters())
		self.setViewOptions(camera.viewOptions())
		self.matchTransforms(camera)
		return True
	
	def pictureRatio(self):
		return self._nativeTypePointer.aspectRatio()

	def setPictureRatio(self, pictureRatio):
		self._nativeTypePointer.setAspectRatio(pictureRatio)
		return True
	
# register the symbol
import cross3d
cross3d.registerSymbol('SceneCamera', MayaSceneCamera)
