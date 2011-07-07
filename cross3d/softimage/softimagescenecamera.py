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
		
	def cache( self, path ):
		# although I am currently using the blur legacy library. Bad!
		# this method does not really belong in api but there is no alternative yet. Bad!
		
		import os
		import blurXSI 
		import blurCamera
		
		outputType = 'Animation'
		sampleType = 'regular'
		sampleRate = 1
		handles = 5
		userProps = self.userProps()
		if 'Range' in userProps:
			range = userProps[ 'Range' ]
		else:
			raise Exception( self.name(), 'has no Range UserProp.' )
			return None
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
		xsi.SetValue( nativeCamera.FullName + ".blurShotProperties.ShotNumber", float( iteration ), "")
		self.setDisplayName( blurName )

		# cache
		blurXSI.fileWrite (	path, outputType , shotNumber , range[0], range[1], sampleType, sampleRate, (range[0] - handles), (range[1] + handles), [nativeCamera] )
		
		# restore camera
		self.setDisplayName( initialName )
		self.deleteProperty( 'blurShotProperties' )

		return True

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', SoftimageSceneCamera )