##
#	\namespace	blur3d.api.softimage.softimagescenecamera
#
#	\remarks	The SotimageSceneCamera class provides the implementation of the AbstractSceneCamera class as it applies
#				to Softimage scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from PySoftimage import xsi
from blur3d.api.abstract.abstractscenecamera import AbstractSceneCamera

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneCamera( AbstractSceneCamera ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def lens( self ):
		return xsi.GetValue( self.name() + '.camera.projplanedist' )
		
	def setLens( self, value ):
		self._nativePointer.Parameters( 'projplanedist' ).Value = value

	def showsFrame( self ):
		return xsi.GetValue( self.name() + '.camvis.currenttime' )
		
	def setShowsFrame( self, switch ):
		xsi.SetValue( self.name() + '.camvis.currenttime', switch )
		return True
		
	def setShowsCustomParameters( self, switch ):
		xsi.SetValue( self.name() + '.camvis.custominfo', switch )
		return True
		
	def setHeadLightIsActive( self, switch ):
		xsi.SetValue( self.name() + '.camdisp.headlight', switch )
		return True
		
	def headlightIsActive( self ):
		return xsi.GetValue( self.name() + '.camdisp.headlight' )
		
	def pictureRatio( self ):
		return self._nativePointer.Parameters( 'aspect' ).Value 
	
	def setPictureRatio( self, pictureRatio ):
		xsi.setValue( self.name() + '.camera.aspect', pictureRatio )
		#self._nativePointer.Parameters( 'aspect' ).Value = pictureRatio
		return True
		
	def farClippingPlane( self ):
		return self._nativePointer.Parameters( 'far' ).Value 
		
	def setFarClippingPlane( self, distance ):
		xsi.setValue( self.name() + '.camera.far', distance )
		#self._nativePointer.Parameters( 'far' ).Value = distance
		return True
		
	def nearClippingPlane( self ):
		return self._nativePointer.Parameters( 'near' ).Value 
		
	def setNearClippingPlane( self, distance ):
		xsi.setValue( self.name() + '.camera.near', distance )
		#self._nativePointer.Parameters( 'near' ).Value = distance
		return True

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', SoftimageSceneCamera )