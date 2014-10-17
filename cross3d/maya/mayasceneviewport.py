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
		self._name = api.SceneWrapper._mObjName(self._nativeCamera())
	
	#--------------------------------------------------------------------------------
	#									Private Methods
	#--------------------------------------------------------------------------------
	def _nativeCamera(self):
		undocumentedPythonFunctionRequirement = om.MDagPath()
		self._nativePointer.getCamera(undocumentedPythonFunctionRequirement)
		return undocumentedPythonFunctionRequirement.node()
		
	def _setNativeCamera(self, nativeCamera):
		nativeCamera = api.SceneWrapper._asMOBject(nativeCamera)
		dagPath = om.MDagPath.getAPathTo(nativeCamera)
		self._nativePointer.setCamera(dagPath)
		# Ensure the viewport is refreshed
		api.application.refresh()
		return True
	#--------------------------------------------------------------------------------
	#									Public Methods
	#--------------------------------------------------------------------------------
	def cameraName(self):
		""" Return the viewport's camera name """
		return self.camera().name()
	
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
		# TODO: Make generating movies not require setting frame padding to 1
		padding = 1
		if not resolution:
			resolution = self._scene.renderSize()
		
		# TODO: Add support for these arguments
		if slate != None:
			# Note: this is probably how we can handle slate
			#cmds.headsUpDisplay( 'blurBurnin', section=8, block=0, blockAlignment='right', dw=50, label='This is my burnin')
			blurdev.debug.debugObject(self.generatePlayblast, 'slate is not implemented in Maya')
		if pathFormat != r'{basePath}\{fileName}.{frame}.{ext}':
			blurdev.debug.debugObject(self.generatePlayblast, 'pathFormat is not implemented in Maya')
		
		# Prepare to detect if the playblast was canceled
		formatter = '{fileName}.{frame:0%i}{ext}' % padding
		lastFrameFileName = formatter.format(fileName=fileName, frame=frameRange[1], ext=ext)
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
		
		
		# MCH 10/16/14 NOTE: Info on parsing playblast Display Menu if we decide to add support for that later
		#--------------------------------------------------------------------------------
		#for i in cmds.optionVar(list=True):
		#	if i.startswith('playblastShow'):
		#		print cmds.optionVar(query=i), i
		#		# Set the value
		#		cmds.optionVar( intValue=(i, False)
		#		# Update the playblast menus
		#		maya.mel.eval('updatePlayblastPluginMenus()')
		#--------------------------------------------------------------------------------
		
		# MCH 10/16/14 NOTE: To query/enable depth of field
		#--------------------------------------------------------------------------------
		# cam = scene.viewport().camera()
		# ntp = cam._nativeTypePointer
		# ntp.isDepthOfField()
		# ntp.setDepthOfField(False)
		#--------------------------------------------------------------------------------
		
		cam = self.camera()
		name = cam.name()
		overscanLocked = cmds.getAttr("{name}.overscan".format(name=cam.name()), lock=True)
		if overscanLocked:
			# unlock overscan if it is locked
			cmds.setAttr("{name}.overscan".format(name=name), lock=False)
		
		# create a StateLocker object to backup the current values before setting them
		with StateLocker() as stateLocker:
			# Currently the state locker isnt the most convienent to use
			def setPropertyLocker(obj, key, value):
				stateLocker.setMethodArgs(obj, obj.setProperty, partial(obj.property, key), key, value)
			
			# Set FilmBack.FitResolutionGate to Overscan
			setPropertyLocker(cam, 'filmFit', 3)
			# uncheck Display Film Gate
			setPropertyLocker(cam, 'displayFilmGate', 0)
			# uncheck Display Resolution
			setPropertyLocker(cam, 'displayResolution', 0)
			# Set overscan to 1.0
			setPropertyLocker(cam, 'overscan', 1.0)
			
			if antiAlias:
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.multiSampleEnable', True)
			
			# Store and restore these settings
			options = ['sel']
			
			# Find the current viewport so we can apply the viewport settings
			panel = cmds.getPanel(withFocus=True)
			# Check for if non-viewport panel's are active
			if not panel in cmds.getPanel(type='modelPanel'):
				panel = 'modelPanel4'
			
			if geometryOnly:
				# HACK: This records the viewport show options, sets them to playblast options, then
				# restores them
				# TODO: Make this load the settings from the playblast overrides
				# Dirty dict to query values
				options.extend(['nurbsCurves', 'nurbsSurfaces', 'cv', 'hulls', 'polymeshes', 
							'subdivSurfaces', 'planes', 'lights', 'cameras', 'imagePlane', 'joints', 
							'ikHandles', 'dynamics', 'deformers', 'fluids', 
							'hairSystems', 'follicles', 'nCloths', 'nParticles', 'nRigids', 
							'dynamicConstraints', 'locators', 'dimensions', 'pivots', 'handles', 
							'textures', 'strokes', 'motionTrails', 'pluginShapes', 'clipGhosts', 
							'greasePencils', 'manipulators', 'grid', 'hud',
							])
				# New features in 2015
				if api.application.version() > 2014:
					options.append('particleInstancers')
			
			# Store the current values
			states = {}
			for option in options:
				states[option] = cmds.modelEditor(panel, query=True, **{option: True})
			
			if geometryOnly:
				# Hide everything but Polygons
				cmds.modelEditor(panel, edit=True, allObjects=False)
				cmds.modelEditor(panel, edit=True, polymeshes=True)
			
			# Hide selection
			cmds.modelEditor(panel, edit=True, sel=False)
			
			# generate playblast
			cmds.playblast(
					width=resolution.width(), 
					height=resolution.height(), 
					startTime=frameRange.start(), 
					endTime=frameRange.end(), 
					percent=100, 
					filename=fileName, 
					showOrnaments=False, 
					format=playblastFormat, 
					compression=compression, 
					quality=quality, 
					framePadding=padding,
					viewer=False)
			
			if geometryOnly:
				# Restore the original values
				for option, value in states.iteritems():
					cmds.modelEditor(panel, edit=True, **{option: value})
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