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
import math
from Py3dsMax import mxs
from PyQt4.QtCore import QSize
from blur3d.constants import CameraType
from blur3d.api.abstract.abstractscenecamera import AbstractSceneCamera

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneCamera( AbstractSceneCamera ):
	
	_outputTypes = ['Still', 'Movie', 'Video']
	_whiteBalances = ['Custom', 'Neutral', 'Daylight', 'D75', 'D65', 'D55', 'D50', 'Temperature']
	_distortionTypes = ['Quadratic', 'Cubic', 'File', 'Texture']
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def cameraType( self ):
		"""
			\remarks	implements the AbstractSceneCamera.cameraType method to determine what type of camera this instance is
			\return		<blur3d.api.constants.CameraType>
		"""
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
		
	def fov(self, rounded=False):
		"""
			\remarks	returns the current FOV of the camera.
			\return		<float>
		"""
		fov = self.nativePointer().fov
		if rounded:
			return int(round(fov))
		return fov
		
	def lens( self, filmWidth=None, rounded=False):
		"""
			\remarks	returns the current lens of the camera.
			\return		<float>
		"""
		if filmWidth:
			fov = math.radians(self.fov())
			lens = (0.5 * float(filmWidth)) / math.tan(fov / 2.0)
		else:
			lens = mxs.cameraFOV.FOVtoMM( self.nativePointer().fov )
		if rounded:
			return int(round(lens))
		return lens
		
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
			
	def outputType(self):
		return self._outputTypes[self._nativePointer.type] if self.isCameraType(CameraType.VRayPhysical) else ''
	
	def setOutputType(self, outputType):
		if isinstance(outputType, basestring) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.type = self._outputTypes.index(outputType)
			return True
		return False
		
	def exposureEnabled(self):
		return self._nativePointer.exposure if self.isCameraType(CameraType.VRayPhysical) else False
	
	def setExposureEnabled(self, exposureEnabled):
		if isinstance(exposureEnabled, (bool, int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.exposure = exposureEnabled
			return True
		return False
	
	def vignettingEnabled(self):
		return self._nativePointer.vignetting if self.isCameraType(CameraType.VRayPhysical) else False

	def setVignettingEnabled(self, vignettingEnabled):
		if isinstance(vignettingEnabled, (bool, int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.vignetting = vignettingEnabled
			return True
		return False

	def whiteBalance(self):
		return self._whiteBalances[self._nativePointer.whiteBalance_preset] if self.isCameraType(CameraType.VRayPhysical) else ''

	def setWhiteBalance(self, whiteBalance):
		if isinstance(whiteBalance, basestring) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.whiteBalance_preset = self._whiteBalances.index(whiteBalance)
			return True
		return False

	def shutterAngle(self):
		return self._nativePointer.shutter_angle if self.isCameraType(CameraType.VRayPhysical) else 180

	def setShutterAngle(self, shutterAngle):
		if isinstance(shutterAngle, (int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.shutter_angle = shutterAngle
			return True
		return False

	def shutterOffset(self):
		return self._nativePointer.shutter_offset if self.isCameraType(CameraType.VRayPhysical) else 0

	def setShutterOffset(self, shutterOffset):
		if isinstance(shutterOffset, (int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.shutter_offset = shutterOffset
			return True
		return False

	def bladesEnabled(self):
		return self._nativePointer.use_blades if self.isCameraType(CameraType.VRayPhysical) else False
	
	def setBladesEnabled(self, bladesEnabled):
		if self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.use_blades = bladesEnabled
			return True
		return False	

	def blades(self):
		return self._nativePointer.blades_number if self.isCameraType(CameraType.VRayPhysical) else 0
	
	def setBlades(self, blades):
		if isinstance(blades, (int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.blades_number = int(blades)
			return True
		return False

	def anisotropy(self):
		return self._nativePointer.anisotropy if self.isCameraType(CameraType.VRayPhysical) else False
	
	def setAnisotropy(self, anisotropy):
		if isinstance(anisotropy, (int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.anisotropy = anisotropy
			return True
		return False

	def distortionType(self):
		return self._distortionTypes[self._nativePointer.distortion_type] if self.isCameraType(CameraType.VRayPhysical) else ''
	
	def setDistortionType(self, distortionType):
		if isinstance(distortionType, basestring) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.distortion_type = self._distortionTypes.index(distortionType)
			return True
		return False

	def distortion(self):
		return self._nativePointer.Distortion if self.isCameraType(CameraType.VRayPhysical) else False
	
	def setDistortion(self, distortion):
		if isinstance(distortion, (int, float)) and self.isCameraType(CameraType.VRayPhysical):
			self._nativePointer.Distortion = distortion
			return True
		return False

	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCamera', StudiomaxSceneCamera )