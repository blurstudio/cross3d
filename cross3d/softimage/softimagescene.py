##
#	\namespace	blur3d.api.softimage.softimagescene
#
#	\remarks	The SoftimageScene class will define all the operations for Softimage scene interaction.  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/01/11
#

from blur3d   							import pendingdeprecation, constants
from PySoftimage 						import xsi, xsiFactory
from blur3d.api.abstract.abstractscene  import AbstractScene
from blurdev.decorators 				import stopwatch

#------------------------------------------------------------------------------------------------------------------------

class SoftimageScene( AbstractScene ):
	def __init__( self ):
		AbstractScene.__init__( self )
		
		# create custom properties
		self._metaData 			= None
		self._mapCache			= None
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _importNativeModel( self, path, name = '' ):
		"""
			\remarks	implements the AbstractScene._importNativeModel to import and return a model in the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		return xsi.ImportModel( path, '', '', '', name )( 'Value' )
		
	def _removeNativeModels( self, models ):
		"""
			\remarks	implements the AbstractScene._removeNativeModels to remove a native model in the scene. Addded by douglas
			\param		models [ <PySoftimage.xsi.Model>, ... ]
			\return		<bool> success
		"""
		self._removeNativeObjects( models )
		return True
		
	def _setNativeSelection( self, selection ):
		"""
			\remarks	implements the AbstractScene._setNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		#import blurdev.debug
		#watch = blurdev.debug.Stopwatch( 'Total' )
		#watch.newLap('Setting Selection')
		xsiCollSelection = xsiFactory.CreateObject( 'XSI.Collection' )
		xsiCollSelection.AddItems( selection )
		xsi.SelectObj( xsiCollSelection )
		#watch.stop()
		return True
		
	def _addToNativeSelection( self, selection ):
		"""
			\remarks	implements the AbstractScene._addToNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		xsiCollSelection = xsiFactory.CreateObject( 'XSI.Collection' )
		xsiCollSelection.AddItems( selection )
		xsi.AddToSelection( selection )
		
	def _nativeRootObject( self ):
		"""
			\remarks	implements the AbstractScene._nativeRoot method to return the native root of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject
		"""
		return xsi.ActiveSceneRoot

	def _removeNativeObjects( self, nativeObjects ):
		"""
			\remarks	implements the AbstractScene._removeNativeObjects method to return the native root of the scene
			\return		<bool> success
		"""
		branchCode = "B:"
		names = []
		for obj in nativeObjects:
			names.append( branchCode + obj.FullName )
		xsi.DeleteObj( ",".join( names ) )
		return True

	@pendingdeprecation
	def _nativeModels( self ):
		"""
			\remarks	implements the AbstractScene._nativeModels method to return the native root of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject
		"""
		models = []
		for obj in self._nativeObjects():
			if "model" in obj.Type.lower():
				models.append( obj )
		return models
	
	def _nativeObjects( self, getsFromSelection=False, wildcard='' ):
		"""
			\remarks	implements the AbstractScene._nativeObjects method to return the native objects from the scene
			\return		<list> [ <PySoftimage.xsi.X3DObject> nativeObject, .. ] || None
		"""
		if getsFromSelection:
#			objects = xsiFactory.CreateObject( 'XSI.Collection' )
#			objects.AddItems( objects )
			objects = [ obj for obj in xsi.Selection ]
			if wildcard:
				import re
				expression = wildcard.replace('*', '.+').strip('.+')
				output = []
				for obj in objects:
					if re.findall( expression, obj.FullName, flags=re.I ):
						output.append( obj )
				return output
		else:
			root = self._nativeRootObject()
			objects = root.FindChildren( wildcard, '', '', True )
		return objects
		
	def _nativeSelection( self, wildcard='' ):
		return self._nativeObjects( getsFromSelection=True, wildcard=wildcard )
	
	def _findNativeObject( self, name='', uniqueId=0 ):
		"""
			\remarks	implements AbstractScene._findNativeObject method to looks up a native object based on the inputed name
			\param		name <string>
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		return xsi.Dictionary.GetObject( name, False )

	def _findNativeCamera( self, name = '', uniqueId = 0 ):
		"""
			\remarks	implements AbstractScene._findNativeObject method to looks up a native camera based on the inputed name
			\param		name <string>
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		obj = xsi.Dictionary.GetObject( name, False )
		if 'camera' in obj.Type.lower():
			return obj
		return None

	def _freezeNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	implements the AbstractScene._freezeNativeObjects method to freeze(lock)/unfreeze(unlock) the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		for object in nativeObjects:
			object.Properties('Visibility').Parameters('selectability').SetValue(not state)
		return True
	
	def _hideNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	implements the AbstractScene._hideNativeObjects method to hide/unhide the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		for object in nativeObjects:
			object.Properties('Visibility').Parameters('viewvis').SetValue(not state)
			object.Properties('Visibility').Parameters('rendvis').SetValue(not state)
		return True
	
	@pendingdeprecation
	def _nativeCameras( self ):
		"""
			\remarks	implements the AbstractScene._nativeCameras method to return the native cameras of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject
		"""
		cameras = []
		for obj in self._nativeObjects():
			if "camera" in obj.Type.lower():
				cameras.append( obj )
		return cameras
		
	def _nativeRenderPasses( self ):
		"""
			\remarks	implements the AbstractScene._nativeRenderPasses that returns the native render passes in the scene
			\return		nativeRenderPasses [ <PySoftimage.xsi.Pass>, <...> ]
		"""	
		return xsi.ActiveProject.ActiveScene.Passes
		
	def _findNativeRenderPass( self, displayName= '' ):
		"""
			\remarks	implements the AbstractScene._findNativeRenderPass that find render passes in the scene based on their display name
			\Param		displayName <string>
			\return		nativeRenderPasses [ <PySoftimage.xsi.Pass>, <...> ]
		"""	
		return self._findNativeObject( "Passes." + displayName )
		
	def _currentNativeRenderPass( self ):
		"""
			\remarks	implements the AbstractScene._currentNativeRenderPass that returns the active render pass in the scene	
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""	
		return xsi.ActiveProject.ActiveScene.ActivePass
		
	def _setCurrentNativeRenderPass( self, nativeSceneRenderPass ):
		"""
			\remarks	implements the AbstractScene._setCurrentNativeRenderPass method to set the current render pass in the scene			\param		displayName			<str>
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""	
		xsi.SetCurrentPass( nativeSceneRenderPass )
		return True
		
	def _removeNativeRenderPasses( self , nativeRenderPasses ):
		"""
			\remarks	implements the AbstractScene._createNativeRenderPass method to create a new Softimage render pass
			\param		displayName			<str>
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""	
		self._removeNativeObjects( nativeRenderPasses )
		return True
		
	def _createNativeRenderPass( self, displayName ):
		"""
			\remarks	implements the AbstractScene._createNativeRenderPass method to create a new Softimage render pass
			\param		displayName			<str>
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""
		self.setSilentMode( True )
		renderPass = xsi.CreatePass("", displayName )( "Value" )
		self.setSilentMode( False )
		return renderPass
		
	def _exportNativeObjectsToFBX( self, nativeObjects, path, frameRange=None, showUI=True ):
		"""
			\remarks	exports a given set of nativeObjects as FBX.
			\return		<bool> success
		"""
		
		# Collecting the controllers we want to plot.
		controllers = []
		for nativeObject in nativeObjects:
			transformsGlobal = nativeObject.Kinematics.Global
			transformsLocal = nativeObject.Kinematics.Local
			for transform in [ 'pos', 'rot', 'scl' ]:
				for axis in 'xyz':
					controllerGlobal = transformsGlobal.Parameters( transform + axis )
					controllerLocal = transformsLocal.Parameters( transform + axis )
					if controllerGlobal.IsAnimated() or controllerLocal.isAnimated():
						controllers.append( controllerLocal )

		# Storing all the stuff we will be doing.
		xsi.OpenUndo( "Plotting and Exporting to FBX" )

		# Defining the range.
		if frameRange:
			self.setAnimationRange( frameRange )

		# Setting the selection.
		self._setNativeSelection( nativeObjects )
		
		# Setting the FBX export options.
		xsi.FBXExportScaleFactor( 1 )
		xsi.FBXExportGeometries( True )
		xsi.FBXExportShapes( True )
		xsi.FBXExportSkins( True )
		xsi.FBXExportCameras( True )
		xsi.FBXExportLights( True )
		xsi.FBXExportDeformerAsSkeleton( False )
		xsi.FBXExportEmbedMedias( False )
		xsi.FBXExportAnimation( True )
		xsi.FBXExportFrameRate( self.animationFPS() )
		xsi.FBXExportKeepXSIEffectors( True )	
		xsi.FBXExportSelection( True )
		
		# Plotting and exporting the FBX File.
		xsi.PlotAndApplyActions( controllers, "plot", frameRange[0], frameRange[1], "", 20, 3, "", "", "", "", True, True )
		xsi.FBXExport( path )

		# Restoring the scene state.
		xsi.CloseUndo()
		xsi.Undo("")
		
		return True
		
	def viewports( self ):
		"""
			\remarks	implements the AbstractScene.viewports method to return the visible viewports
			\return		[ <blur3d.api.SceneViewport>, ... ]
		"""
		from blur3d.api import SceneViewport
		viewportNames = SceneViewport.viewportNames
		viewportLetters = [ viewportNames[ key ] for key in viewportNames.keys() ]
		viewportLetters = sorted( viewportLetters )
		viewports = []
		viewManager = xsi.Desktop.ActiveLayout.Views( 'vm' )
		for letter in viewportLetters:
			if not viewManager.GetAttributeValue( 'layout:%s' % letter ) == 'hidden':
				number = viewportLetters.index( letter ) + 1
				viewports.append( SceneViewport( self, number ) )
		return viewports
		
	def _createNativeModel( self, name = 'Model', nativeObjects = [] ):
		"""
			\remarks	implements the AbstractScene._createNativeModel method to return a new Softimage model
			\param		name			<str>
			\return		<PySoftimage.xsi.Model> nativeModel
		"""
		root = self._nativeRootObject()
		return root.addModel( nativeObjects, name )
		
	def _createNativeCamera( self, name = 'Camera', type = 'Standard' ):
		"""
			\remarks	implements the AbstractScene._createNativeCamera method to return a new Softimage camera
			\param		name			<str>
			\return		<PySoftimage.xsi.Camera> nativeCamera
		"""
		root = self._nativeRootObject()
		return root.addCamera( 'Camera', name )
		
	def _exportNativeModel( self, nativeModel, path ):
		"""
			\remarks	implements the AbstractScene._exportNativeModel method to export a Softimage model
			\param		nativeModel <PySoftimage.xsi.Model>
			\param		path <string>
		"""
		xsi.ExportModel( nativeModel, path, "", "" )
		return True
	
	def _isolateNativeObjects( self, nativeObjects ):
		selection = self._nativeSelection()
		self._setNativeSelection( nativeObjects )
		xsi.IsolateSelected()
		self._setNativeSelection( selection )
		return True
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def cacheXmesh(self, path, objList, start, end, worldLock, stack = 3, saveVelocity = True, ignoreTopology  = True):
		"""
			\remarks	runXmesh cache function
			\param		models [ <SceneModel>, ... ]
			\return		<bool> success
		"""
		mesh = xsi.Export_XMesh(objList, stack, start, end, path, worldLock)
		return True
	
	def loadFile( self, filename = '' , confirm = True):
		"""
			\remarks	loads the inputed filename into the application, returning true on success
			\param		filename	<str>
			\return		<bool> success
		"""
		xsi.OpenScene( filename, confirm)
		return False
		
	def animationRange( self ):
		"""
			\remarks	implements AbstractScene.animationRange method to return the current animation start and end frames
			\return		<blur3d.api.FrameRange>
		"""
		from blur3d.api import FrameRange
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		return FrameRange( [ int( playControl.Parameters( "In" ).Value ), int( playControl.Parameters( "Out" ).Value ) ] )

	def animationFPS( self ):
		"""
			\remarks	implements AbstractScene.animationFPS method to return the current frame per second rate.
			\return		<float> fps
		"""
		return float( xsi.ActiveProject.Properties( "Play Control" ).Parameters( "Rate" ).Value )
	
	@classmethod
	def currentFileName( cls ):
		"""
			\remarks	implements AbstractScene.currentFileName method to return the current filename for the scene that is active in the application
			\return		<str>
		"""
		return xsi.ActiveProject.ActiveScene.FileName.Value
	
	def currentFrame( self ):
		"""
			\remarks	implements AbstractScene.currentFrame method to return the current frame
			\return		<int>
		"""
		return int( xsi.ActiveProject.Properties( "Play Control" ).Parameters( "Current" ).Value )

	def setCurrentFrame( self, frame ):
		"""
			\remarks	implements AbstractScene.setCurrentFrame method to set the current frame
			\return		<bool> success
		"""
		xsi.ActiveProject.Properties( "Play Control" ).Parameters( "Current" ).Value = frame
		return True
		
	def clearSelection( self ):
		"""
			\remarks	implements AbstractScene.clearSelection method to clear the selection in the scene.
			\return		<bool> success
		"""
		xsi.DeselectAll()
		return True

	def setAnimationFPS(self, fps, changeType=constants.FPSChangeType.Frames):
		"""
			\remarks	Updates the scene's fps to the provided value and scales existing keys as specified.
			\param		fps 		<float>
			\param		changeType	<constants.FPSChangeType>	Defaults to constants.FPSChangeType.Frames
			\return		<bool> success
		"""
		playControl = xsi.ActiveProject.Properties('Play Control')
		# Only update the change timing if it needs to change
		current = playControl.Parameters('KeepFrameTiming').Value
		if current and changeType == constants.FPSChangeType.Seconds:
			playControl.Parameters('KeepFrameTiming').Value = 0 # seconds
		elif not current and changeType == constants.FPSChangeType.Frames:
			playControl.Parameters('KeepFrameTiming').Value = 1 # frames
		playControl.Parameters('Format').Value = 11 # switch to custom format 
		playControl.Parameters('Rate').Value = fps
		return True

	def setAnimationRange( self, animationRange ):
		"""
			\remarks	implements AbstractScene.setAnimationRange method to set the current start and end frame for animation
			\param		animationRange	<tuple> ( <int> start, <int> end )
			\return		<bool> success
		"""
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		playControl.Parameters( "In" ).Value = animationRange[0]
		playControl.Parameters( "Out" ).Value = animationRange[1]
		playControl.Parameters( "GlobalIn" ).Value = animationRange[0]
		playControl.Parameters( "GlobalOut" ).Value = animationRange[1]
		return True
		
	def setSilentMode( self, switch ):
		"""
			\remarks	implements AbstractScene.setAutoInspect method to set the Auto Inspect state
			\param		switch	<bool>
			\return		<bool> success
		"""
		if switch:
			xsi.SetValue("preferences.scripting.cmdlog", False, "")
			xsi.SetValue( "preferences.Interaction.autoinspect", False, "" )
		else:
			xsi.SetValue( "preferences.Interaction.autoinspect", True, "" )
			xsi.SetValue("preferences.scripting.cmdlog", True, "")
		return True
			
	def retime( self, offset, scale = 1, activeRange = None, pivot = None ):
		if activeRange:
			if not pivot:
				pivot = activeRange[0]
		else:
			activeRange = ( -9999, 9999 )
			if not pivot:
				pivot = 1
		xsi.SISequence( "", "siAllAnimParams", offset, scale, activeRange[0], activeRange[1], activeRange[0], "siFCurvesAnimationSources" )
		return True	
		
	def setTimeControlPlay( self, switch, fromStart=False ):
		if switch:
			if fromStart:
			    xsi.PlayRealTimeFromStart()
			else:
				xsi.PlayRealTime()
		else:
			xsi.PlaybackStop()
		return True
			
	def setTimeControlLoop( self, switch ):
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		playControl.Parameters( "Loop" ).Value = switch
		return True
		
	def isTimeControlLoop( self ):
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		return playControl.Parameters( "Loop" ).Value
		
	def undo( self ):
		"""
			\remarks	undos the last action.
			\return		<bool>
		"""
		xsi.Undo( '' )
		return True
	
# register the symbol
from blur3d import api
api.registerSymbol( 'Scene', SoftimageScene )