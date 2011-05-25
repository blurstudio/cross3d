##
#	\namespace	blur3d.api.softimage.softimagescene
#
#	\remarks	The SoftimageScene class will define all the operations for Softimage scene interaction.  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/01/11
#

from PySoftimage import xsi
from blur3d.api.abstract.abstractscene import AbstractScene

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
	
	def _importNativeModel( self, path, name = '' ): # double check documentation
		"""
			\remarks	implements the AbstractScene._importNativeModel to import and return a model in the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		return xsi.ImportModel( path, '', '', '', name )( 'Value' )
		
	def _nativeSelection( self ):
		"""
			\remarks	implements the AbstractScene._nativeSelection to return the native selected objects of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		return xsi.Selection
		
	def _setNativeSelection( self, selection ):
		"""
			\remarks	implements the AbstractScene._setNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		if ( not selection ):
			xsi.DeselectAll()
		else:
			xsi.SelectObj( selection )
		return True
		
	def _addToNativeSelection( self, selection ):
		"""
			\remarks	implements the AbstractScene._addToNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
			\return		<bool> success
		"""
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
	
	def _nativeObjects( self ):
		"""
			\remarks	implements the AbstractScene._nativeObjects method to return the native objects from the scene
			\return		<list> [ <PySoftimage.xsi.X3DObject> nativeObject, .. ] || None
		"""
		root = self._nativeRootObject()
		return root.FindChildren( '', '', '', True )
	
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
		return xsi.ActiveProject.ActiveScene.Passes
		
	def _findNativeRenderPass( self, displayName= '' ):
		return self._findNativeObject( "Passes." + displayName )
		
	def _currentNativeRenderPass( self ):
		return xsi.ActiveProject.ActiveScene.ActivePass
		
	def _setCurrentNativeRenderPass( self, nativeSceneRenderPass ):
		xsi.SetCurrentPass( nativeSceneRenderPass )
		return True
		
	def _removeNativeRenderPasses( self , nativeRenderPasses ): 
		self._removeNativeObjects( nativeRenderPasses )
		return True
		
	def _createNativeRenderPass( self, displayName ): 
		return xsi.CreatePass("", displayName )( "Value" )
		
	def _exportNativeModel( self, nativeModel, path ): # not in abstract
		xsi.ExportModel( nativeModel, path, "", "" )
		return True
			
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def animationRange( self ):
		"""
			\remarks	implements AbstractScene.animationRange method to return the current animation start and end frames
			\return		<tuple> (<int> startFrame,<int> endFrame>)
		"""
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		return [ int( playControl.Parameters( "In" ).Value ), int( playControl.Parameters( "Out" ).Value ) ]

	def animationFPS( self ): # not in abstract
		"""
			\remarks	implements AbstractScene.animationFPS method to return the current frame per second rate.
			\return		<int> endFrame>
		"""
		return xsi.ActiveProject.Properties( "Play Control" ).Parameters( "Rate" ).Value
		
	def currentFileName( self ):
		"""
			\remarks	implements AbstractScene.currentFileName method to return the current filename for the scene that is active in the application
			\return		<str>
		"""
		return xsi.ActiveProject.ActiveScene.FileName.Value
	
	def currentFrame( self ): # not in abstract
		"""
			\remarks	implements AbstractScene.currentFrame method to return the current frame
			\return		<int>
		"""
		return int( xsi.ActiveProject.Properties( "Play Control" ).Current.Value )

	def setCurrentFrame( self, frame ): # not in abstract
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
		
	def setAnimationRange( self, animationRange ): # I think we need to add a switch for global local at every level
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
			xsi.SetValue( "preferences.Interaction.autoinspect", False, "" )
		else:
			xsi.SetValue( "preferences.Interaction.autoinspect", True, "" )
		return True
		
	def getAvailableIteration( self, mask ): # not in abstract
		import string
		for iteration in string.uppercase:
			if not self._findNativeObject( mask % { "iteration" : iteration } ):
				return iteration
		return None
		
	def isAvalaibleName( self, name ): # not in abstract
		if self._findNativeObject( name ):
			return False
		else:
			return True
			
	def offsetAnimation( self, value ): # not in abstract
		self.setSilentMode( True )
		xsi.SISequence( "", "siAllAnimParams", value, "", 1, 100, 1, "siFCurvesAnimationSources" )
		for model in self.models():
			if model.assetType() == "camera":
				camera = self.findCamera( model.name() + '.View' )
				if camera:
					camera.offsetRange( value )
		self.setSilentMode( False )
		return True	
		
	def setTimeControlPlay( self, switch, fromStart=False ): # not in abstract
		if switch:
			if fromStart:
			    xsi.PlayRealTimeFromStart()
			else:
				xsi.PlayRealTime()
		else:
			xsi.PlaybackStop()
		return True
			
	def setTimeControlLoop( self, switch ): # not in abstract
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		playControl.Parameters( "Loop" ).Value = switch
		return True
		
	def isTimeControlLoop( self ): # not in abstract
		playControl = xsi.ActiveProject.Properties( "Play Control" )
		return playControl.Parameters( "Loop" ).Value
		
	def currentViewport( self ): # not in abstract
		viewportManager = xsi.Desktop.ActiveLayout.Views( "vm" )
		viewportName = viewportManager.GetAttributeValue( "focusedviewport" )
		from blur3d.api import SceneViewport
		return SceneViewport( viewportName )

	def softwareVersion( self ):
		print xsi.version()
		
	def softwareName( self ):
		return "Softimage"
		
	def undo( self ):
		xsi.Undo( '' )
		return True
		
	def exportModel( self, model, path ): # not in abstract
		nativeModel = model.nativePointer()
		return self._exportNativeModel( nativeModel, path )

# register the symbol
from blur3d import api
api.registerSymbol( 'Scene', SoftimageScene )