##
#	\namespace	blur3d.api.studiomax.studiomaxscenecamera
#
#	\remarks	The StudiomaxSceneCamera class provides the implementation of the AbstractSceneCamera class as it applies
#				to 3d Studio Max scenes
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

import os
from Py3dsMax import mxs
from PyQt4.QtCore import QSize
from blur3d.api.abstract.abstractscenecamera import AbstractSceneCamera

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneCamera( AbstractSceneCamera ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def cameraType( self ):
		"""
			\remarks	implements the AbstractSceneCamera.cameraType method to determine what type of camera this instance is
			\return		<blur3d.api.constants.CameraType>
		"""
		from blur3d.constants import CameraType
		
		cls = mxs.classof(self._nativePointer)
		if ( cls in (mxs.FreeCamera,mxs.TargetCamera) ):
			return CameraType.Standard
		
		elif ( cls == mxs.VRayPhysicalCamera ):
			return CameraType.VRayPhysical
		return 0

	def filmWidth(self):
		"""
			\remarks	Returns the film_width of the camera.
			\return		film_width (float)
		"""
		try:
			fw = self._nativePointer.film_width
		except AttributeError:
			return None
		return fw
		
	def lens( self ):
		"""
			\remarks	returns the current lens of the camera.
			\return		<float>
		"""
		return mxs.cameraFOV.FOVtoMM( self.nativePointer().fov )
		
	def hasMultiPassEffects( self ):
		"""
			\remarks	returns whether multipass effects are active on this camera
			\return		<bool>
		"""
		if mxs.isProperty( self._nativePointer, 'mpassEnabled' ):
			return self._nativePointer.mpassEnabled
		return False
		
	def renderMultiPassEffects( self ):
		"""
			\remarks	runs the multipass effects on this camera
			\return		<bool>
		"""
		mxs.maxOps.displayActiveCameraViewWithMultiPassEffect()
		return True
		
	def generateRender( self, **options ):
		"""
			\remarks	renders an image sequence form that camera with the current render settings
			\param 		path <String>
			\param 		frameRange <blur3d.api.FrameRange>
			\param 		resolution <QtCore.QSize>
			\param 		pixelAspect <float>
			\param 		step <int>
			\param 		missingFramesOnly <bool>
			\return		<blur3d.api.constants.CameraType>
		"""
		
		path = options.get( 'path', '' )
		resolution = options.get( 'resolution', QSize( mxs.renderWidth, mxs.renderHeight ) )
		pixelAspect = options.get( 'pixelAspect', 1.0 )
		step = options.get( 'step', 1 )
		frameRange = options.get( 'frameRange', [] )
		missingFramesOnly = options.get( 'missingFramesOnly', False )
			
		if path:
			basePath = os.path.split(path)[0]
			if not os.path.exists( basePath ):
				os.makedirs( basePath )
		
		if frameRange:
			bitmap = mxs.render( outputFile=path, fromFrame=frameRange[0], toFrame=frameRange[1], camera=self._nativePointer, nthFrame=step, outputWidth=resolution.width(), outputHeight=resolution.height(), pixelAspect=pixelAspect )
			mxs.undisplay( bitmap )
		else:
			bitmap = mxs.render( outputFile=path, frame=mxs.pyHelper.namify( 'current' ), camera=self._nativePointer, outputWidth=resolution.width(), outputHeight=resolution.height(), pixelAspect=pixelAspect )	

	def setFilmWidth(self, width):
		"""
			\remarks	Sets the film_width value for the camera.
			\param		width <float>
			\return		n/a
		"""
		try:
			self._nativePointer.film_width = float(width)
		except AttributeError:
			pass
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', StudiomaxSceneCamera )