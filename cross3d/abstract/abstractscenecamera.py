##
#	\namespace	blur3d.api.abstract.abstractsceneobject
#
#	\remarks	The AbstractSceneObject class provides the base foundation for the 3d Object framework for the blur3d system
#				This class will provide a generic overview structure for all manipulations of 3d objects
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneObject

class AbstractSceneCamera( SceneObject ):

	@abstractmethod
	def cameraType( self ):
		"""
			\remarks	return the camera type for this camera instance
			\return		<blur3d.constants.CameraType>
		"""
		return 0

	def isCameraType( self, cameraType ):
		"""
			\remarks	return whether or not this camera is a kind of the inputed camera type
			\sa			cameraType
			\param		cameraType	<blur3d.constants.CameraType>
			\return		<blur3d.constants.CameraType>
		"""
		return (self.cameraType() & cameraType) > 0

	@abstractmethod
	def lens( self ):
		return 0.0

	@abstractmethod
	def setLens( self, value ):
		return False
	
	@abstractmethod	
	def showCurrentFrame( self, switch ):
		return False

	@abstractmethod
	def showCustomParameters( self, switch ):
		return False

	@abstractmethod
	def setHeadlight( self, switch ):
		return False

	@abstractmethod
	def hasHeadlight( self ):
		return False
		
	@abstractmethod
	def hasEffect( self ):
		return False

	@abstractmethod
	def renderEffect( self ):
		return False

	@abstractmethod
	def cache( self, path ):
		"""
			\remarks	caches the camera using .xsi format. Does not belon in api. Added by douglas
			\param		path <str>
			\return		<bool> success
		"""
		return False
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', AbstractSceneCamera, ifNotFound = True )