import glob
import os
from functools import partial
import blurdev
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omUI
from blur3d import api
from blur3d.api import Exceptions
from blur3d.api.classes import FrameRange
from blur3d.api.abstract.abstractsceneviewport import AbstractSceneViewport

from blur3d.lib.statelockerlib import StateLocker

#------------------------------------------------------------------------------------------------------------------------

class MayaSceneViewport(AbstractSceneViewport):
	# From the Docs:
	# To determine which settings are available on your system, use the `playblast -options` 
	# command. This will display a system-specific dialog with supported compression formats.
	_validPlayblastFormats = ['gif', 'si', 'rla', 'tif', 'tifu', 'sgi', 'als', 'maya', 'jpg', 
			'eps', 'cin', 'yuv', 'tga', 'bmp', 'psd', 'png', 'dds', 'psdLayered', 'avi', 'mov']
	
	def __init__( self, scene, viewportID=None ): 
		super(MayaSceneViewport, self).__init__(scene, viewportID)
		
		if viewportID == None:
			self._nativePointer = omUI.M3dView.active3dView()
		else:
			self._nativePointer = omUI.M3dView()
			omUI.M3dView.get3dView(viewportID, self._nativePointer)
		self._name = self.camera().displayName()
	
	#--------------------------------------------------------------------------------
	#									Private Methods
	#--------------------------------------------------------------------------------
	def _nativeCamera(self):
		undocumentedPythonFunctionRequirement = om.MDagPath()
		self._nativePointer.getCamera(undocumentedPythonFunctionRequirement)
		return undocumentedPythonFunctionRequirement.node()
		
	def _setNativeCamera(self, nativeCamera):
		dagPath = om.MDagPath.getAPathTo(nativeCamera)
		self._nativePointer.setCamera(dagPath)
		return True
	#--------------------------------------------------------------------------------
	#									Public Methods
	#--------------------------------------------------------------------------------
	def cameraName(self):
		""" Return the viewport's camera name """
		return self.camera().displayName()
	
	def createCamera(self, name='Camera', type='Standard'):
		""" Creates a camera that matches that viewport. """
		camera = self._scene.createCamera(name, type)
		camera.matchCamera(self.camera())
		return camera
	
	def generatePlayblast(
				self, 
				fileName, 
				frameRange=None, 
				resolution=None, 
				slate=None, 
				effects=True, 
				geometryOnly=True, 
				antiAlias=False, 
				pathFormat=r'{basePath}\{fileName}.{frame}.{ext}'):
		fileName, ext = os.path.splitext(fileName)
		# Make sure a invalid file format was not requested
		if ext.replace('.', '').lower() not in self._validPlayblastFormats:
			raise Exceptions.FileFormatNotSupported('The file format {ext} is not supported by Maya'.format(ext=ext))
		
		playblastFormat = 'image'
		compression = ext.replace('.', '')
		quality = 100
		if ext.lower() == '.mov':
			playblastFormat = 'qt'
		elif ext.lower() == '.avi':
			playblastFormat = 'avi'
			compression = None
		
		if isinstance(frameRange, int):
			frameRange = FrameRange([frameRange, frameRange])
		if not frameRange:
			frameRange = self._scene.animationRange()
		if not resolution:
			resolution = self._scene.renderSize()
		
		# TODO: Add support for these arguments
		if slate != None:
			# Note: this is probably how we can handle slate
			#cmds.headsUpDisplay( 'blurBurnin', section=8, block=0, blockAlignment='right', dw=50, label='This is my burnin')
			blurdev.debug.debugObject(self.generatePlayblast, 'slate is not implemented in Maya')
		if not effects:
			blurdev.debug.debugObject(self.generatePlayblast, 'effects is not implemented in Maya')
		if antiAlias:
			blurdev.debug.debugObject(self.generatePlayblast, 'antiAlias is not implemented in Maya')
		if pathFormat != r'{basePath}\{fileName}.{frame}.{ext}':
			blurdev.debug.debugObject(self.generatePlayblast, 'pathFormat is not implemented in Maya')
		
		# Prepare to detect if the playblast was canceled
		lastFrameFileName = '{fileName}.{frame:04}{ext}'.format(fileName=fileName, frame=frameRange[1], ext=ext)
		try:
			lastFrameStartTime = os.path.getmtime(lastFrameFileName)
		except os.error:
			lastFrameStartTime = 0
		
		# to properly generate a playblast
		# pass the width/height to the playblast command
		# set the camera displayOptions
		#	set overscan to 1.0 and lock it
		# 	uncheck all options
		# set camera\Film Back
		#	Fit Resolution Gate to overscan
		# 	set proper film aspect ratio?
		# set the render resolution?
		
		cam = self.camera()
		name = cam.name()
		overscanLocked = cmds.getAttr("{name}.overscan".format(name=cam.name()), lock=True)
		if overscanLocked:
			# unlock overscan if it is locked
			cmds.setAttr("{name}.overscan".format(name=name), lock=False)
		
		# create a StateLocker object to backup the current values before setting them
		with StateLocker() as stateLocker:
			# Set FilmBack.FitResolutionGate to Overscan
			stateLocker.setMethodArgs(cam, cam.setProperty, partial(cam.property, 'filmFit'), 'filmFit', 3)
			# set Aspect Ratio
#			stateLocker.setMethod(cam, cam.setPictureRatio, cam.pictureRatio, 2.35)
			# uncheck Display Film Gate
			stateLocker.setMethodArgs(cam, cam.setProperty, partial(cam.property, 'displayFilmGate'), 'displayFilmGate', 0)
			# uncheck Display Resolution
			stateLocker.setMethodArgs(cam, cam.setProperty, partial(cam.property, 'displayResolution'), 'displayResolution', 0)
			# Set overscan to 1.0
			stateLocker.setMethodArgs(cam, cam.setProperty, partial(cam.property, 'overscan'), 'overscan', 1.0)
			# generate playblast
			cmds.playblast(width=resolution.width(), height=resolution.height(), startTime=frameRange.start(), endTime=frameRange.end(), 
							percent=100, filename=fileName, showOrnaments=False, format=playblastFormat, 
							compression=compression, quality=quality, viewer=False)
		if overscanLocked:
			# relock overscan
			cmds.setAttr("{name}.overscan".format(name=name), lock=True)
		
		# No way to detect if a avi or quicktime was canceled
		if ext.lower() in ('.mov', '.avi'):
			return True
		
		# If the capture was not completed we just return False.
		try:
			lastFrameEndTime = os.path.getmtime(lastFrameFileName)
			if not lastFrameStartTime < lastFrameEndTime:
					return False
		except os.error:
			return False
		return True
	
	def refresh(self):
		self._nativePointer.refresh(False, True)

# register the symbol
api.registerSymbol('SceneViewport', MayaSceneViewport)