import glob
import os
from functools import partial
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omUI
import cross3d
from cross3d import Exceptions, ExceptionRouter
from cross3d.classes import FrameRange
from cross3d.abstract.abstractsceneviewport import AbstractSceneViewport

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
		self._name = cross3d.SceneWrapper._mObjName(self._nativeCamera())
	
	#--------------------------------------------------------------------------------
	#									Private Methods
	#--------------------------------------------------------------------------------
	def _nativeCamera(self):
		undocumentedPythonFunctionRequirement = om.MDagPath()
		with ExceptionRouter():
			self._nativePointer.getCamera(undocumentedPythonFunctionRequirement)
			return undocumentedPythonFunctionRequirement.node()
		
	def _setNativeCamera(self, nativeCamera):
		nativeCamera = cross3d.SceneWrapper._asMOBject(nativeCamera)
		with ExceptionRouter():
			dagPath = om.MDagPath.getAPathTo(nativeCamera)
		self._nativePointer.setCamera(dagPath)
		# Ensure the viewport is refreshed
		cross3d.application.refresh()
		return True
	#--------------------------------------------------------------------------------
	#									Public Methods
	#--------------------------------------------------------------------------------
	def cameraName(self):
		""" Return the viewport's camera name """
		return self.camera().path()
	
	def createCamera(self, name='Camera', type='Standard'):
		""" Creates a camera that matches that viewport. """
		camera = self._scene.createCamera(name, type)
		camera.matchCamera(self.camera())
		# Default cameras are hidden. Force the camera visible
		camera.setHidden(False)
		return camera
	
	def generatePlayblast(
				self, 
				fileName, 
				frameRange=None, 
				resolution=None, 
				slate=None, 
				effects=True, 
				geometryOnly=True, 
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
			cross3d.logger.debug('slate is not implemented in Maya')
		if pathFormat != r'{basePath}\{fileName}.{frame}.{ext}':
			cross3d.logger.debug('pathFormat is not implemented in Maya')
		
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
		
		cam = self.camera()
		name = cam.path()
		overscanLocked = cmds.getAttr("{name}.overscan".format(name=cam.path()), lock=True)
		if overscanLocked:
			# unlock overscan if it is locked
			cmds.setAttr("{name}.overscan".format(name=name), lock=False)
		
		# create a StateLocker object to backup the current values before setting them
		from blur3d.lib.statelockerlib import StateLocker
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
			
			# Store and restore these settings using modelEditor
			# The key is the property to query/edit, the value is the value used while playblasting
			modelEditorOverrides = {'sel':False}
			
			# Find the current viewport so we can apply the viewport settings
			panel = cmds.getPanel(withFocus=True)
			# Check for if non-viewport panel's are active
			if not panel in cmds.getPanel(type='modelPanel'):
				panel = 'modelPanel4'
			
			if geometryOnly:
				modelEditorOverrides['nurbsSurfaces'] = True
				modelEditorOverrides['polymeshes'] = True
				modelEditorOverrides['subdivSurfaces'] = True
				# HACK: This records the viewport show options, sets them to playblast options, then
				# restores them
				# TODO: Make this load the settings from the playblast overrides
				attrs = ['nurbsCurves', 'nurbsSurfaces', 'cv', 'hulls', 'polymeshes', 
						'subdivSurfaces', 'planes', 'lights', 'cameras', 'imagePlane', 'joints', 
						'ikHandles', 'dynamics', 'deformers', 'fluids', 'hairSystems', 'follicles', 
						'nCloths', 'nParticles', 'nRigids', 'dynamicConstraints', 'locators', 
						'dimensions', 'pivots', 'handles', 'textures', 'strokes', 'motionTrails', 
						'pluginShapes', 'clipGhosts', 'greasePencils', 'manipulators', 'grid', 'hud']
				# Disable display of all of these options as long as modelEditorOverrides doesnt 
				# already contain a setting key
				updateDict = dict([(attr, False) for attr in attrs if attr not in modelEditorOverrides])
				modelEditorOverrides.update(updateDict)
				# New features in 2015
				if cross3d.application.version() > 2014 and 'particleInstancers' not in modelEditorOverrides:
					modelEditorOverrides.update(particleInstancers=False)
			
			if effects == True:
				modelEditorOverrides.update(displayTextures=True, displayLights='all')
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.ssaoEnable', 1)
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.motionBlurEnable', 1)
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.multiSampleEnable', True)
				
				# TODO: Add Camera.setDeptOfField to cross3d
				ntp = cam._nativeTypePointer
				stateLocker.setMethod(ntp, ntp.setDepthOfField, ntp.isDepthOfField, True)
				
			if effects == False:
				modelEditorOverrides.update(displayTextures=False, displayLights='default')
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.ssaoEnable', 0)
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.motionBlurEnable', 0)
				setPropertyLocker(self._scene, 'hardwareRenderingGlobals.multiSampleEnable', False)
				
				# TODO: Add Camera.setDeptOfField to cross3d
				ntp = cam._nativeTypePointer
				stateLocker.setMethod(ntp, ntp.setDepthOfField, ntp.isDepthOfField, False)
			
			# Store the current values
			modelEditorStates = {}
			for option, value in modelEditorOverrides.iteritems():
				# Store  the current value
				modelEditorStates[option] = cmds.modelEditor(panel, query=True, **{option: True})
				# Set the playblast value
				cmds.modelEditor(panel, edit=True, **{option: value})
			
#			# Uncomment this code to update the ui so you can see what options get disabled in the toolbar
#			from PyQt4.QtGui import QApplication, QMessageBox
#			QApplication.processEvents()
#			QMessageBox.question(None, 'Temp', 'update')
			
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
			
			# Restore the modelEditor options to their previous value
			for option, value in modelEditorStates.iteritems():
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
cross3d.registerSymbol('SceneViewport', MayaSceneViewport)
