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
	
	def range( self ):
		metadata = self.metadata()
		return metadata.attribute( 'range' )

	def lens( self ):
		return self.nativePointer().Parameters( 'projplanedist' ).Value
		
	def setLens( self, value ):
		self.nativePointer().Parameters( 'projplanedist' ).Value = value
		
	def setRange( self, range ):
		metadata = self.metadata()
		metadata.setAttribute( 'range', range )
		return True
		
	def showCurrentFrame( self, switch ):
		xsi.SetValue( self.name() + '.camvis.currenttime', switch )
		return True
		
	def showCustomParameters( self, switch ):
		xsi.SetValue( self.name() + '.camvis.custominfo', switch )
		return True
		
	def setHeadlight( self, switch ):
		xsi.SetValue( self.name() + '.camdisp.headlight', switch )
		return True
		
	def hasHeadlight( self ):
		return xsi.GetValue( self.name() + '.camdisp.headlight' )

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', SoftimageSceneCamera )