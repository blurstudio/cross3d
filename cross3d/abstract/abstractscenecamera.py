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

from blurdev import debug
from blur3d.api import SceneObject

class AbstractSceneCamera( SceneObject ):
	def cameraType( self ):
		"""
			\remarks	[abstract] return the camera type for this camera instance
			\return		<blur3d.constants.CameraType>
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
			
		return 0
	
	def isCameraType( self, cameraType ):
		"""
			\remarks	return whether or not this camera is a kind of the inputed camera type
			\sa			cameraType
			\param		cameraType	<blur3d.constants.CameraType>
			\return		<blur3d.constants.CameraType>
		"""
		return (self.cameraType() & cameraType) > 0
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', AbstractSceneCamera, ifNotFound = True )