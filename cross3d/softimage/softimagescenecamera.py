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
		return self.nativePointer().Parameters( 'projplanedist' ).Value
		
	def setLens( self, value ):
		self.nativePointer().Parameters( 'projplanedist' ).Value = value

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
		
	def generateDotXSI( self, path, range=None ):
		import os
		import blurXSI 
		import blurCamera
		
		outputType = 'Animation'
		sampleType = 'regular'
		sampleRate = 1
		handles = 5
		nativeCamera = self.nativePointer()
		start = str( range[0] )
		end = str( range[1] )	
		initialName = self.displayName()
		model = self.model()
		iteration = model.iteration()
		if not type( iteration ) in [ float, int ]:
			raise Exception( model.name(), 'does not describe a shot number.' )
			return None	
		blurCamIteration = model.iterationString( 4, 2, '-', True )
		blurName = '_'.join( [ 'S', blurCamIteration, '', start + '-' + end, '' ] )
		shotNumber = float( iteration )

		# adding the blur properties and setting the name of the camera
		blurCamera.AddBlurPropertyToCamera( nativeCamera, False );
		xsi.SetValue( nativeCamera.FullName + ".blurShotProperties.StartFrame", range[0], "")
		xsi.SetValue( nativeCamera.FullName + ".blurShotProperties.EndFrame", range[1], "")
		xsi.SetValue( nativeCamera.FullName + ".blurShotProperties.ShotNumber", shotNumber, "")
		self.setDisplayName( blurName )

		# write the file
		blurXSI.fileWrite( path, outputType , shotNumber , range[0], range[1], sampleType, sampleRate, (range[0] - handles), (range[1] + handles), [nativeCamera] )
		
		# restore camera
		self.setDisplayName( initialName )
		self.deleteProperty( 'blurShotProperties' )

		return True

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', SoftimageSceneCamera )