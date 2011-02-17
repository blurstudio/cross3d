##
#	\namespace	blur3d.api.abstract.abstractscene
#
#	\remarks	The AbstractScene class will define all the operations for scene interaction.  Everything for the 3d abstraction layer of the blur3d
#				package will access information from a Scene instance.  This way, you can have a reference to a Studiomax scene, a Softimage scene, a
#				Proxy scene, whatever, and access all generic object, layer, material information in the same way
#
#				The AbstractScene is a QObject instance and any changes to scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as [abstract] will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All [abstract] methods MUST be implemented
#				in a subclass.
#
#				The term NativeObject will be used when referring to methods and pointers referencing an application specific instance (Studiomax vs. Softimage
#				for example) vs. one of the blur3d's wrapper objects (SceneObject,SceneLayer,etc.)
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blurdev import debug
from PyQt4.QtCore import QObject, pyqtSignal

class AbstractScene( QObject ):
	# layer signals
	layerStateChanged			= pyqtSignal()
	layerCreated				= pyqtSignal('PyQt_PyObject')
	layerRenamed				= pyqtSignal('PyQt_PyObject')
	layerRemoved 				= pyqtSignal('PyQt_PyObject')
	layerGroupCreated			= pyqtSignal('str')
	layerGroupRemoved			= pyqtSignal('str')
	
	# create the scene instance
	_instance = None
	
	def __init__( self ):
		QObject.__init__( self )
		
		# create custom properties
		self._updatesDisabled 	= 0
		self._materialCache		= None
		self._mapCache			= None
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _cacheNativeMap( self, cacheType, nativeMap ):
		"""
			\remarks	[abstract] cache the inputed map in the scene
			\param		cacheType	<blur3d.constants.MapCacheType>
			\param		nativeMap	<variant>
			\return		<bool> changed
		"""		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
			
		return nativeMap
	
	def _cacheNativeMaterial( self, cacheType, nativeMaterial ):
		"""
			\remarks	[abstract] cache the inputed material in the scene
			\param		cacheType	<blur3d.constants.MaterialCacheType>
			\param		nativeMaterial	<variant>
			\return		<bool> changed
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _cachedNativeMap( self, cacheType, mapId, default = None ):
		"""
			\remarks	[abstract] return the cached map for the inputed material id
			\param		cacheType	<blur3d.constants.MapCacheType>
			\param		mapId		<str>
			\param		default		<variant>	value to return if the id was not found
			\return		<variant> nativeMap || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return default
	
	def _cachedNativeMaterial( self, cacheType, materialId, default = None ):
		"""
			\remarks	[abstract] return the cached material for the inputed material id
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\param		materialId		<str>
			\param		default			<variant>	value to return if the id was not found
			\return		<variant> nativeMaterial || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return default
	
	def _cachedNativeMaps( self, cacheType ):
		"""
			\remarks	[abstract] return the cached maps for the inputed cache type
			\param		cacheType	<blur3d.constants.MapCacheType>
			\return		<list> [ <variant> nativeMap, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _cachedNativeMaterials( self, cacheType ):
		"""
			\remarks	[abstract] return the cached materials for the inputed cache type
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _clearNativeMaterialOverride( self, nativeObjects ):
		"""
			\remarks	[abstract] clear the native objects of any material overrides
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	def _clearNativePropSetOverride( self, nativeObjects ):
		"""
			\remarks	[abstract] clear the native objects of any property set overrides
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	def _createNativeLayer( self, name, nativeObjects = [] ):
		"""
			\remarks	[abstract]		creates a new layer in this scene based on the inputed name with the given objects
			\param		name			<str>
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<variant> nativeLayer || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _createNativeLayerGroup( self, name, nativeLayers = [] ):
		"""
			\remarks	[abstract]		create a new layer group in this scene based on the inputed name with the given layers
			\param		name			<str>
			\return		<variant> nativeLayerGroup || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
		
	def _createNativeModel( self, name = 'New Model', nativeObjects = [] ):
		"""
			\remarks	[abstract] 		creates and returns a new 3d model with the inputed name and objects
			\param		name			<str>
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<variant> nativeObject || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
		
	def _createNativeRenderer( self, rendererType ):
		"""
			\remaks		[abstract]		creates a new renderer based on the inputed renderer type for this scene
			\param		rendererType	<blur3d.constants.RendererType>
			\return		<variant> nativeRenderer || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _currentNativeRenderer( self ):
		"""
			\remarks	[abstract]	return the current native renderer for this scene instance
			\return		<variant> nativeRenderer || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _exportNativeObjects( self, nativeObjects ):
		"""
			\remarks	[abstract]			exports the inputed native objects to the given filename
			\param		nativeObjects		<list> [ <variant> nativeObject, .. ]
			\param		filename			<str>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _findNativeAtmospheric( self, atmosName = '', atmosId = 0 ):
		"""
			\remarks	[abstract] look up the native atmospheric from this scene instance
			\param		atmosName	<str>
			\return		<variant> nativeAtmospheric || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _findNativeObject( self, objectName = '', objectId = 0 ):
		"""
			\remarks	[abstract] looks up an object based on the inputed name
			\sa			findNativeObject
			\param		objectName	<str>
			\return		<variant> nativeObject || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _findNativeLayer( self, layerName = '', layerId = 0 ):
		"""
			\remarks	[abstract] looks up a layer based on the inputed name
			\sa			findNativeLayer
			\param		layerName	<str>
			\return		<variant> nativeLayer || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _findNativeLayerGroup( self, groupName = '', groupId = 0):
		"""
			\remarks	[abstract] look up a layer group based on the inputed name
			\sa			findNativeLayer
			\param		layerName	<str>
			\return		<variant> nativeLayerGroup || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _findNativeMaterial( self, materialName = '', materialId = 0 ):
		"""
			\remarks	[abstract] looks up an material based on the inputed name
			\sa			findNativeMaterial
			\param		materialName	<str>
			\return		<variant> nativeMaterial || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _findNativeMap( self, mapName = '', mapId = 0 ):
		"""
			\remarks	[abstract] looks up an map based on the inputed name
			\sa			findNativeMap
			\param		mapName	<str>
			\return		<variant> nativeMap || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _freezeNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	[abstract]		freeze(lock)/unfreeze(unlock) a list of native objects
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _fromNativeValue( self, nativeValue ):
		"""
			\remarks	[virtual] 	converts the inputed value from a native value from whatever application we're in
			\param		nativeValue		<variant>
			\return		<variant>
		"""
		# by default, we assume all conversions have already occurred
		return nativeValue
	
	def _getNativeObject( self ):
		"""
			\remarks	[abstract]	invokes the application's ability to let a user select a Object from the scene
			\return		<variant> nativeObject || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
		
	def _getNativeMaterial( self ):
		"""
			\remarks	[abstract]	invokes the application's ability to let a user select a Material from the scene
			\return		<variant> nativeMaterial || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
		
	def _getNativeMap( self ):
		"""
			\remarks	[abstract]	invokes the application's ability to let a user select a Map from the scene
			\return		<variant> nativeMap || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
		
	def _hideNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	[abstract]		hide/unhide a list of native objects
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _isolateNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	[abstract] isolate (hide all other objects) or unisolate the inputed objects in the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _loadNativeMaterialsFromLibrary( self, filename = '' ):
		"""
			\remarks	[abstract] loads a bunch of materials from the inputed library location, or prompts the user to select a library when not provided
			\param		filename	<str>
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeActiveLayer( self ):
		"""
			\remarks	[abstract]		returns the native active layer from the scene
			\param		name			<str>
			\return		<variant> nativeLayer || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _nativeAtmospherics( self ):
		"""
			\remarks	[abstract]	return the native atmospheric instances for this scene
			\return		<list> [ <variant> nativeAtmospheric, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeCameras( self ):
		"""
			\remarks	[abstract] return a collection of the cameras in this scene
			\return		<list> [ <variant> nativeCamera, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeCustomProperty( self, key, default = None ):
		"""
			\remarks	[abstract] return the native property for the inputed key
			\param		key			<str>
			\param		default		<variant>
			\return		<variant>
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return default
		
	def _nativeEnvironmentMap( self ):
		"""
			\remarks	[abstract] return the current scene environment map
			\return		<variant> nativeMap || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _nativeEnvironmentMapOverride( self ):
		"""
			\remarks	[abstract] return the current scene environment map override
			\return		<variant> nativeMap || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _nativeRefresh( self ):
		"""
			\remarks	[abstrct]	refreshes the contents of the current scene
			\sa			setUpdatesEnabled, update
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _nativeLayers( self ):
		"""
			\remarks	[abstract]		returns a list of the native layers in this scene
			\return		<list> [ <variant> nativeLayer, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeLayerGroups( self ):
		"""
			\remarks	[abstract] collect all the layer groups and their corresponding layers
			\sa			layerGroups
			\return		<list> [ <variant> nativeLayerGroup, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeMaterials( self ):
		"""
			\remarks	[abstract] collect all the materials in this scene
			\sa			materials
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeMaps( self ):
		"""
			\remarks	[abstract] collect all the maps in this scene
			\sa			maps
			\return		<list> [ <variant> nativeMap, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeObjects( self ):
		"""
			\remarks	[abstract] 	returns the native objects from the scene
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeRootObject( self ):
		"""
			\remarks	[abstract] 	returns the native root object of the scen
			\return		<variant> nativeObject || None
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeSelection( self ):
		"""
			\remarks	[abstract] 	returns the selected objects from the scene
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeWorldLayer( self ):
		"""
			\remarks	[abstract]		returns the native world layer from the scene
			\param		name			<str>
			\return		<variant> nativeLayer
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _removeNativeObjects( self, nativeObjects ):
		"""
			\remarks	[abstract]		removes the inputed objects from the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _renameNativeObjects( self, nativeObjects, names, display = True ):
		"""
			\remarks	[abstract]		removes the inputed objects from the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		names			<list> [ <str> name, .. ]
			\param		display		<bool> 	tags whether or not the names are display names or object names
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setCachedNativeMaps( self, cacheType, nativeMaps ):
		"""
			\remarks	[abstract] set the currently cached maps for the inputed cache type
			\param		cacheType	<blur3d.constants.MapCacheType>
			\param		nativeMaps	<list> [ <variant> nativeMap, .. ]
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setCachedNativeMaterials( self, cacheType, nativeMaterials ):
		"""
			\remarks	[abstract] set the currently cached materials for the inputed cache type
			\param		cacheType			<blur3d.constants.MaterialCacheType>
			\param		nativeMaterials		<list> [ <variant> nativeMaterial, .. ]
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setCurrentNativeRenderer( self, nativeRenderer ):
		"""
			\remarks	[abstract] set the current renderer to the inputed native renderer
			\param		nativeRenderer	<variant>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeCustomProperty( self, key, value ):
		"""
			\remarks	[abstract] set the custom property on this scene to the inputed value
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeMaterialOverride( self, nativeObjects, nativeMaterial, options = None ):
		"""
			\remarks	[abstract] set the material override for the inputed objects
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		nativeMaterial	<variant>
			\param		options			<blur3d.constants.MaterialOverrideOptions>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeEnvironmentMap( self, nativeMap ):
		"""
			\remarks	[abstract] set the current environment map in the scene
			\param		nativeMap	<variant>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeEnvironmentMapOverride( self, nativeMap ):
		"""
			\remarks	[abstract] set the current environment map override in the scene
			\param		nativeMap	<variant>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativePropSetOverride( self, nativeObjects, nativePropSet ):
		"""
			\remarks	[abstract] set the overriding property set for the inputed objects to the given property set
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		nativePropSet	<variant>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeSelection( self, nativeObjects ):
		"""
			\remarks	[abstract]		selects the inputed native objects in the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeUpdatesEnabled( self, state ):
		"""
			\remarks	[abstract]		enables/disables scene updates
			\param		state		<bool>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _toNativeValue( self, pyValue ):
		"""
			\remarks	[virtual] 	converts the inputed value from Qt/Python to whatever value is required for the native application
			\param		pyValue	<variant>
			\return		<variant>
		"""
		from PyQt4.QtCore import QString
		
		# we should not pass back QString value's to an application, as they will not expect it.  Standard python strings/unicodes will be auto-converted
		if ( type(pyValue) == QString ):
			return unicode(pyValue)
		
		# by default, we assume that any other type can be naturally processed
		return pyValue
	
	def _toggleNativeVisibleState( self, nativeObjects = None, options = None ):
		"""
			\remarks	[abstract] toggle the inputed object's visibility settings based on the inputed options
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		options			<blur3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _visibleNativeObjects( self ):
		"""
			\remarks	[abstract]		returns the visible objects in the scene
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def activeLayer( self ):
		"""
			\remarks	returns the currently active layer of the scene
			\return		<blur3d.api.SceneLayer> || None
		"""
		lay = self._nativeActiveLayer()
		if ( lay ):
			from blur3d.api import SceneLayer
			return SceneLayer( self, lay )
		return None
	
	def atmospherics( self ):
		"""
			\remarks	returns the atmospheric instances from this scene
			\return		<list> [ <blur3d.api.SceneAtmospheric>, .. ]
		"""
		from blur3d.api import SceneAtmospheric
		nativeAtmos = self._nativeAtmospherics()
		return [ SceneAtmospheric( self, atmos ) for atmos in nativeAtmos ]
	
	def cacheMap( self, cacheType, sceneMap ):
		"""
			\remarks	cache the inputed map in the scene for the given cache type
			\sa			_cacheNativeMap
			\param		cacheType	<blur3d.constants.MapCacheType>
			\param		sceneMap	<blur3d.api.SceneMap>
			\return		<bool> success
		"""
		return self._cacheNativeMap( cacheType, sceneMap.nativePointer() )
	
	def cacheMaterial( self, cacheType, material ):
		"""
			\remarks	cache the inputed material in the scene for the given cache type
			\sa			_cacheNativeMaterial
			\param		cacheType	<blur3d.constants.MaterialCacheType>
			\param		material	<blur3d.api.SceneMaterial>
			\return		<bool> success
		"""
		return self._cacheNativeMaterial( cacheType, material.nativePointer() )
	
	def cachedMap( self, cacheType, mapId, default = None ):
		"""
			\remarks	return the cached map given the inputed id
			\sa			_cachedNativeMap
			\param		cacheType	<blur3d.constants.MapCacheType>
			\param		mapId		<str>
			\param		default		<variant>	default return value if not found
			\return		<blur3d.api.SceneMap> || None
		"""
		nativeMap =  self._cachedNativeMap( cacheType, mapId )
		if ( nativeMap ):
			from blur3d.api import SceneMap
			return SceneMap( self, nativeMap )
		return None
	
	def cachedMaps( self, cacheType ):
		"""
			\remarks	return the cached maps for this scene for the given cache type
			\sa			_cachedNativeMaps
			\param		cacheType		<blur3d.constants.MapCacheType>
			\return		<list> [ <blur3d.api.SceneMap> map, .. ]
		"""
		from blur3d.api import SceneMap
		return [ SceneMap( self, nativeMap ) for nativeMap in self._cachedNativeMaps( cacheType ) ]
	
	def cachedMaterial( self, cacheType, materialId, default = None ):
		"""
			\remarks	return the cached material given the inputed id
			\sa			_cachedNativeMaterial
			\param		cacheType	<blur3d.constants.MaterialCacheType>
			\param		materialId	<str>
			\param		default		<variant>	default return value if not found
			\return		<blur3d.api.SceneMaterial> || None
		"""
		nativeMaterial = self._cachedNativeMaterial( cacheType, materialId, default = default )
		if ( nativeMaterial ):
			from blur3d.api import SceneMaterial
			return SceneMaterial( self, nativeMaterial )
		return None
	
	def cachedMaterials( self, cacheType ):
		"""
			\remarks	return the cached materials for this scene given the inputed cache type
			\sa			_cachedNativeMaterials
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\return		<list> [ <blur3d.api.SceneMaterial> material, .. ]
		"""
		from blur3d.api import SceneMaterial
		return [ SceneMaterial( self, material ) for material in self._cachedNativeMaterials( cacheType ) if material != None ]
	
	def cameras( self ):
		"""
			\remarks	return a list of all the camera objects in this scene
			\sa			_nativeCameras
			\return		<list> [ <blur3d.api.SceneCamera>, .. ]
		"""
		from blur3d.api import SceneCamera
		return [ SceneCamera( self, nativeCamera ) for nativeCamera in self._nativeCameras() ]
	
	def checkForSave( self ):
		"""
			\remarks	[abstract]	checks the state of the current scene and queries the user to save if the scene is modified.  If the user cancels the operation,
									this method will return false.  Returns true if the scene is saved, or otherwise is approved by the user to continue the next operation
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def clearMaterialOverride( self, objects ):
		"""
			\remarks	clear the inputed objects of any material overrides that are applied
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._clearNativeMaterialOverride( [ obj.nativePointer() for obj in objects ] )
	
	def clearPropSetOverride( self, objects ):
		"""
			\remarks	clear the inputed objects of any property set overrides that are applied
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._clearNativePropSetOverride( [ obj.nativePointer() for obj in objects ] )
	
	def clearSelection( self ):
		"""
			\remarks	clears the selection in the scene
			\sa			setSelection
			\return		<bool> success
		"""
		return self.setSelection( [] )
	
	def createRenderer( self, rendererType ):
		"""
			\remarks	create a new renderer of the inputed type
			\param		rendererType	<blur3d.constants.RendererType>
			\return		<blur3d.api.Renderer>
		"""
		nativeRenderer = self._createNativeRenderer( rendererType )
		if ( nativeRenderer ):
			from blur3d.api import SceneRenderer
			return SceneRenderer( self, nativeRenderer )
		return None
	
	def createLayer( self, name, objects = [] ):
		"""
			\remarks	creates a new layer with the inputed name and returns it
			\param		name 		<str>
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\return		<blur3d.api.SceneLayer> || None
		"""
		lay = self._createNativeLayer( name, nativeObjects = [ obj.nativePointer() for obj in objects ] )
		if ( lay ):
			from blur3d.api import SceneLayer
			layer = SceneLayer( self, lay )
			self.layerCreated.emit( layer )
			return layer
		return None
	
	def createLayerGroup( self, name, layers = [] ):
		"""
			\remarks	create a new group of layers with the inputed names
			\sa			layerGroups, _createNativeLayerGroup
			\param		name		<str>
			\param		layers		<list> [ <blur3d.api.SceneLayer>, .. ]
			\return		<blur3d.api.SceneLayerGroup> || None
		"""
		nativeGroup = self._createNativeLayerGroup( name, nativeLayers = [ layer.nativePointer() for layer in layers ] )
		if ( nativeGroup ):
			from blur3d.api import SceneLayerGroup
			return SceneLayerGroup( self, nativeGroup )
		return None
		
	def createModel( self, name = 'New Model', objects = [] ):
		"""
			\remarks	creates a new layer with the inputed name and returns it
			\return		<blur3d.api.SceneObject> || None
		"""
		nativeModel = self._createNativeModel( name = name, nativeObjects = [ obj.nativePointer() for obj in objects ] )
		if ( nativeModel ):
			from blur3d.api import SceneObject
			return SceneObject( self, nativeModel )
		return None
	
	def currentLayerState( self ):
		"""
			\remarks	records the current layer state to xml and returns the string
			\return		<str> layerState
		"""
		from blurdev.XML import XMLDocument
		doc = XMLDocument()
		self.recordLayerState( doc )
		return doc.toxml()
		
	def currentFileName( self ):
		"""
			\remarks	[abstract]	returns the current filename for the scene that is active in the application
			\return		<str>
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return ''
	
	def currentRenderer( self ):
		"""
			\remarks	return the current renderer assigned to this scene
			\return		<blur3d.api.SceneRenderer> || None
		"""
		nativeRenderer = self._currentNativeRenderer()
		if ( nativeRenderer ):
			from blur3d.api import SceneRenderer
			return SceneRenderer( self, nativeRenderer )
		return None
	
	def customProperty( self, key, default = None ):
		"""
			\remarks	return a custom property in the scene with the given key
			\return		<variant>
		"""
		return self._fromNativeValue( self._nativeCustomProperty( key, default ) )
	
	def emitLayerStateChanged( self ):
		"""
			\remarks	emits the layerStateChanged signal provided signals are not blocked
		"""
		if ( not self.signalsBlocked() ):
			self.layerStateChanged.emit()
	
	def environmentMap( self ):
		"""
			\remarks	return the current environment map from the scene
			\sa			setEnvironmentMap, _nativeEnvironmentMap
			\return		<blur3d.api.SceneMap> || None
		"""
		nativeMap = self._nativeEnvironmentMap()
		if ( nativeMap ):
			from blur3d.api import SceneMap
			return SceneMap( self, nativeMap )
		return None
	
	def environmentMapOverride( self ):
		"""
			\remarks	return the current environment map override for this scene
			\sa			setEnvironmentMapOverride, _nativeEnvironmentOverride
			\return		<blur3d.api.SceneMap> || None
		"""
		nativeMap = self._nativeEnvironmentMapOverride()
		if ( nativeMap ):
			from blur3d.api import SceneMap
			return SceneMap( self, nativeMap )
		return None
	
	def freezeObjects( self, objects, state ):
		"""
			\remarks	locks/freezes the inputed nodes based on the state
			\sa			_freezeNativeObjects
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\param		state		<bool>
			\return		<bool> success
		"""
		return self._freezeNativeObjects( [ obj.nativePointer() for obj in objects ], state )
	
	def findAtmospheric( self, atmosName = '', atmosId = 0 ):
		"""
			\remarks	look up an atmospheric based on the inputed name
			\sa			_findNativeAtmospheric
			\param		atmosName	<str>
			\return		<blur3d.api.SceneAtmospheric> || None
		"""
		nativeAtmos = self._findNativeAtmospheric( atmosName, atmosId )
		if ( nativeAtmos ):
			from blur3d.api import SceneAtmospheric
			return SceneAtmospheric( self, nativeAtmos )
		return None
	
	def findLayer( self, layerName = '', layerId = 0 ):
		"""
			\remarks	looks up a layer based on the inputed name
			\sa			_findNativeLayer
			\param		layerName	<str>
			\return		<blur3d.api.SceneLayer> || None
		"""
		nativeLayer = self._findNativeLayer( layerName, layerId )
		if ( nativeLayer ):
			from blur3d.api import SceneLayer
			return SceneLayer( self, nativeLayer )
		return None
	
	def findLayerGroup( self, groupName = '', groupId = 0):
		"""
			\remarks	look up a layer group based on the inputed name
			\sa			_findNativeLayerGroup
			\param		groupName	<str>
			\return		<blur3d.api.SceneLayerGroup> || None
		"""
		nativeLayerGroup = self._findNativeLayerGroup( groupName, groupId )
		if ( nativeLayerGroup ):
			from blur3d.api import SceneLayerGroup
			return SceneLayerGroup( self, nativeLayerGroup )
		return None
	
	def findObject( self, objectName = '', objectId = 0 ):
		"""
			\remarks	looks up an individual object by its name
			\sa			_findNativeObject
			\param		objectName	<str>
			\return		<blur3d.api.SceneObject> || None
		"""
		nativeObject = self._findNativeObject( objectName, objectId )
		if ( nativeObject ):
			from blur3d.api import SceneObject
			return SceneObject( self, nativeObject )
		return None
	
	def findMaterial( self, materialName = '', materialId = 0 ):
		"""
			\remarks	looks up an individual material by its name
			\sa			_findNativeMaterial
			\param		materialName	<str>
			\return		<blur3d.api.SceneMaterial> || None
		"""
		if ( self._materialCache != None ):
			mtl = self._materialCache['id'].get(materialId)
			if ( not mtl ):
				mtl = self._materialCache['name'].get(materialName)
			return mtl
		else:
			nativeMaterial = self._findNativeMaterial( materialName, materialId )
			if ( nativeMaterial ):
				from blur3d.api import SceneMaterial
				return SceneMaterial( self, nativeMaterial )
			return None
		
	def findMap( self, mapName = '', mapId = 0 ):
		"""
			\remarks	looks up an individual map by its name
			\sa			_findNativeMap
			\param		mapName	<str>
			\return		<blur3d.api.SceneMap> || None
		"""
		if ( self._mapCache != None ):
			m = self._mapCache['id'].get(mapId)
			if ( not m ):
				m = self._mapCache['name'].get(mapName)
			return m
		else:
			nativeMap = self._findNativeMap( mapName, mapId )
			if ( nativeMap ):
				from blur3d.api import SceneMap
				return SceneMap( self, nativeMap )
			return None
		
	def fileType( self ):
		"""
			\remarks	[abstract]	returns the main file type for this type of application
			\return		<str>
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return ''
		
	def fileTypes( self ):
		"""
			\remarks	[abstract]	returns the associated file types for this type of application
			\return		<list> [ <str>, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def getObject( self ):
		"""
			\remarks	invokes the application's ability to let a user select an Object from the scene
			\return		<blur3d.api.Object> || None
		"""
		from blur3d.api import SceneObject
		object = self._getNativeObject()
		if ( object ):
			return SceneObject( self, object )
		return None
	
	def getMaterial( self ):
		"""
			\remarks	invokes the application's ability to let a user select a Material from the scene
			\return		<blur3d.api.SceneMaterial> || None
		"""
		from blur3d.api import SceneMaterial
		mtl = self._getNativeMaterial()
		if ( mtl ):
			return SceneMaterial( self, mtl )
		return None
		
	def getMap( self ):
		"""
			\remarks	invokes the application's ability to let a user select a Material from the scene
			\return		<blur3d.api.SceneMaterial> || None
		"""
		from blur3d.api import SceneMap
		nativeMap = self._getNativeMap()
		if ( nativeMap ):
			return SceneMap( self, nativeMap )
		return None
	
	def holdCurrentState( self ):
		"""
			\remarks	[abstract]	protects the current scene as it is to allow for manipulation and provide a restore point
			\sa			restoreHeldState
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
	
	def hideObjects( self, objects, state ):
		"""
			\remarks	hides the inputed objects based on the given state
			\sa			_hideNativeObjects
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\param		state		<bool>
			\return		<bool> success
		"""
		return self._hideNativeObjects( [ obj.nativePointer() for obj in objects ], state )
	
	def isEnvironmentMapOverridden( self ):
		"""
			\remarks	checks to see if the current environment map is in an overridden state
			\return		<bool> overridden
		"""
		return self._nativeEnvironmentMapOverride() != None
	
	def isolateObjects( self, objects, state ):
		"""
			\remarks	isolates (hides all other objects) or unisolates the inputed objects in the scene
			\sa			_isolateNativeObjects
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\param		state		<bool>
			\return		<bool> success
		"""
		return self._isolateNativeObjects( [ obj.nativePointer() for obj in objects ], state )
	
	def layers( self ):
		"""
			\remarks	collects all the layers in the scene and returns them
			\sa			createLayer, findLayer
			\return		<list> [ <blur3d.api.SceneLayer>, .. ]
		"""
		from blur3d.api import SceneLayer
		return [ SceneLayer( self, nativeLayer ) for nativeLayer in self._nativeLayers() ]
	
	def layerGroups( self ):
		"""
			\remarks	collect all the layer groups and their corresponding layers
			\sa			createLayerGroup, findLayerGroup
			\return		<dict> { <str> groupName: <list> [ <blur3d.api.SceneLayer>, .. ], .. }
		"""
		from blur3d.api import SceneLayerGroup
		return [ SceneLayerGroup( self, nativeLayerGroup ) for nativeLayerGroup in self._nativeLayerGroups() ]
	
	def loadFile( self, filename = '' ):
		"""
			\remarks	[abstract]	loads the inputed filename into the application, returning true on success
			\param		filename	<str>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def loadMaterialsFromLibrary( self, filename = '' ):
		"""
			\remarks	loads all the materials from a given material library file
			\param		filename	<str>
			\return		<list> [ <blur3d.api.SceneMaterial> ]
		"""
		from blur3d.api import SceneMaterial
		return [ SceneMaterial( self, nativeMaterial ) for nativeMaterial in self._loadNativeMaterialsFromLibrary( filename ) ]
	
	def materials( self ):
		"""
			\remarks	returns a list of all the materials in the scene wrapped as SceneMaterials
			\return		<list> [ <blur3d.api.SceneMaterial>, .. ]
		"""
		from blur3d.api import SceneMaterial
		return [ SceneMaterial( self, obj ) for obj in self._nativeMaterials() ]
	
	def maps( self ):
		"""
			\remarks	returns a list of all the maps in the scene wrapped as SceneMaps
			\return		<list> [ <blur3d.api.SceneMap>, .. ]
		"""
		from blur3d.api import SceneMap
		return [ SceneMap( self, obj ) for obj in self._nativeMaps() ]
	
	def objects( self ):
		"""
			\remarks	returns a list of all the objects in the scene wrapped as SceneObjects
			\return		<list> [ <blur3d.api.SceneObject>, .. ]
		"""
		from blur3d.api import SceneObject
		return [ SceneObject( self, obj ) for obj in self._nativeObjects() ]
	
	def property( self, key, default = None ):
		"""
			\remarks	[abstract]	returns a global scene value
			\param		key			<str> || <QString>
			\param		default		<variant>	default value to return if no value was found
			\return		<variant>
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return default
	
	def recordLayerState( self, xml ):
		"""
			\remarks	records the layer state to XML text
			\sa			restoreLayerState, SceneLayer.recordLayerState
			\return		<str>
		"""
		layerState 	= xml.addNode( 'layerState' )
		layers		= self.layers()
		for layer in layers:
			layer.recordLayerState( layerState )
	
	def restoreLayerState( self, xml ):
		"""
			\remarks	restores the layer state from the inputed XML text
			\sa			recordLayerState, SceneLayer.restoreLayerState
			\return		<bool> success
		"""
		watch = debug.Stopwatch( 'AbstractScene.restoreLayerState' )
		
		layerState = xml.findChild( 'layerState' )
		if ( not layerState ):
			watch.stop()
			return False
		
		watch.startLap( 'Mapping Layers' )
		# create a layer mapping
		layers 			= self.layers()
		layernamemap 	= {}
		layeridmap		= {}
		for layer in layers:
			layernamemap[ str(layer.layerName()) ] 	= layer
			layeridmap[ str(layer.layerId()) ] 		= layer
		watch.stopLap()
		
		# create a material caching
		watch.startLap( 'Caching Materials' )
		materials		= self.materials()
		materialcache	= { 'name': {}, 'id': {} }
		for material in materials:
			materialcache[ 'name' ][ material.materialName() ] 	= material
			materialcache[ 'id' ][ material.materialId() ] 		= material
		
		self._materialCache = materialcache
		watch.stopLap()
		
		# create a map caching
		watch.startLap( 'Caching Maps' )
		maps			= self.maps()
		mapcache		= { 'name': {}, 'id': {} }
		for m in maps:
			mapcache[ 'name' ][ m.mapName() ] 	= map
			mapcache[ 'id' ][ m.mapId() ] 		= map
		
		self._mapCache = mapcache
		watch.stopLap()
		
		# create the progress dialog
		from PyQt4.QtGui import QProgressDialog
		progress = QProgressDialog( 'Loading State', '', 0, len(layers) + 1 )
		progress.setWindowTitle( 'Loading Layer State' )
		progress.show()
		
		# go through the layers in the xml layer state mapping found layers to the scene layers
		processed = []
		for i, layerXml in enumerate(layerState.children()):
			# store the recorded name
			name = layerXml.attribute( 'name' )
			
			# update the progress dialog
			progress.setValue(i)
			progress.setLabelText( 'Loading %s...' % name )
			
			# lookup the layer by name
			if ( name in layernamemap ):
				layer = layernamemap[name]
				watch.startLap( 'Restoring %s' % name )
				layer.restoreLayerState( layerXml )
				watch.stopLap()
				processed.append(layer)
				continue
			
			# lookup the layer by id
			lid = layerXml.attribute( 'id' )
			if ( name in layeridmap ):
				layer = layeridmap[name]
				watch.startLap( 'Restoring %s' % name )
				layer.restoreLayerState( layerXml )
				watch.stopLap()
				processed.append(layer)
				continue
		
		# next hide all the layers taht are not part of the state
		unprocessed = [ layer for layer in layers if not layer in processed ]
		progress.setValue( 1 )
		progress.setMaximum( len(unprocessed) + 1 )
		for i, layer in enumerate(unprocessed):
			progress.setValue(i+1)
			progress.setLabelText( 'Hiding %s...' % layer.layerName() )
			
			watch.startLap( 'Hiding %s' % layer.layerName() )
			layer.setVisible(False)
			watch.stopLap()
		
		self._materialCache = None
		self._mapCache 		= None
		
		watch.stop()
		
		return True
	
	def removeObjects( self, objects ):
		"""
			\remarks	removes the objects from the scene
			\sa			_removeNativeObjects
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._removeNativeObjects( [ obj.nativePointer() for obj in objects ] )
	
	def renameObjects( self, objects, names, display = True ):
		"""
			\remarks	renames the inputed objects to the inputed names
			\sa			_renameNativeObjects
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\param		names		<list> [ <str>, .. ]
			\param		display		<bool> 	tags whether or not the names are display names or object names
			\return		<bool> success
		"""
		return self._renameNativeObjects( [ object.nativePointer() for object in objects ], names, display = display )
	
	def reset( self ):
		"""
			\remarks	[abstract]	resets this scene for all the data and in the application
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def restoreHeldState( self ):
		"""
			\remarks	[abstract]	restores a held state after processing code
			\sa			holdCurrentState
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def rootObject( self ):
		"""
			\remarks	returns the root object of the scene
			\return		<blur3d.api.SceneObject> || None
		"""
		native = self._nativeRootObject()
		if ( native ):
			from blur3d.api import SceneObject
			return SceneObject( self, native )
		return None
	
	def saveFile( self ):
		"""
			\remarks	saves the current file
			\return		<bool> success
		"""
		return self.saveFileAs( self.currentFilename() )
		
	def saveFileAs( self, filename = '' ):
		"""
			\remarks	[abstract]	saves the current scene to the inputed name specified.  If no name is supplied, then the user should be prompted to pick a filename
			\param		filename 	<str>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def selection( self ):
		"""
			\remarks	returns the currently selected objects from the scene
			\sa			_nativeSelection
			\return		<list> [ <blur3d.api.SceneObject>, .. ]
		"""
		from blur3d.api import SceneObject
		return [ SceneObject( self, obj ) for obj in self._nativeSelection() ]
	
	def setEnvironmentMap( self, sceneMap ):
		"""
			\remarks	set the current environment map in the scene to the inputed map
			\sa			environmentMap, _setNativeEnvironmentMap
			\param		sceneMap		<blur3d.api.SceneMap>
			\return		<bool> success
		"""
		nativeMap = None
		if ( sceneMap ):
			nativeMap = sceneMap.nativePointer()
			
		return self._setNativeEnvironmentMap( nativeMap )
	
	def setEnvironmentMapOverride( self, sceneMap ):
		"""
			\remarks	override the current environment map in the scene to the inputed map
			\sa			setEnvironmentMap, _setNativeEnvironmentMapOverride
			\param		sceneMap		<blur3d.api.SceneMap>
			\return		<bool> success
		"""
		nativeMap = None
		if ( sceneMap ):
			nativeMap = sceneMap.nativePointer()
		
		return self._setNativeEnvironmentMapOverride( nativeMap )
	
	def setCachedMapAt( self, cacheType, index, sceneMap ):
		"""
			\remarks	set the cached map for this scene at the inputed index to the given map
			\param		cacheType		<blur3d.constants.MapCacheType>
			\param		index			<int>
			\param		sceneMap		<blur3d.api.SceneMap> || None
			\return		<bool> success
		"""
		nativeMaps = self._cachedNativeMaps( cacheType )
		if ( 0 <= index and index < len(nativeMaps) ):
			nativeMap = None
			if ( sceneMap ):
				nativeMap = sceneMap.nativePointer()
				
			nativeMaps[index] = sceneMap
			self._setCachedNativeMaps( cacheType, nativeMaps )
			return True
		return False
	
	def setCachedMaps( self, cacheType, sceneMaps ):
		"""
			\remarks	set the cached maps for this scene for the given cacheType
			\param		cacheType		<blur3d.constants.MapCacheType>
			\param		sceneMaps		<list> [ <blur3d.api.SceneMap> map, .. ]
			\return		<bool> success
		"""
		return self._setCachedNativeMaps( [ sceneMap.nativePointer() for sceneMap in sceneMaps ] )
	
	def setCachedMaterialAt( self, cacheType, index, material ):
		"""
			\remarks	set the cached material for this scene at the inputed index to the given material
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\param		index			<int>
			\param		material		<blur3d.api.SceneMaterial> || None
			\return		<bool> success
		"""
		nativeMaterials = self._cachedNativeMaterials( cacheType )
		if ( 0 <= index and index < len(nativeMaterials) ):
			nativeMaterial = None
			if ( material ):
				nativeMaterial = material.nativePointer()
			
			nativeMaterials[index] = material
			self._setCachedNativeMaterials( cacheType, nativeMaterials )
			return True
		return False
	
	def setCachedMaterials( self, cacheType, materials ):
		"""
			\remarks	set the cached materials for this scene for the given cacheType
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\param		materials		<list> [ <blur3d.api.SceneMaterial> material, .. ]
			\return		<bool> success
		"""
		return self._setCachedNativeMaterials( cacheType, [ material.nativePointer() for material in materials ] )
	
	def setCurrentLayerState( self, layerState ):
		"""
			\remarks	restore the layer state from the inputed xml string
			\param		layerState	<str>
			\return		<bool> success
		"""
		# create a stopwatch
		watch = debug.Stopwatch( 'AbstractScene.setCurrentLayerState' )
		
		from blurdev.XML import XMLDocument
		doc = XMLDocument()
		
		watch.startLap( 'Parsing State' )
		doc.parse(layerState)
		watch.stopLap()
		
		watch.startLap( 'Restoring Layer State' )
		result = self.restoreLayerState(doc)
		watch.stopLap()
		watch.stop()
		
		return result
	
	def setCurrentRenderer( self, renderer ):
		"""
			\remarks	set the current scene renderer to this class type
			\param		renderer	<blur3d.api.SceneRenderer>
			\return		<bool> success
		"""
		nativeRenderer = None
		if ( renderer ):
			nativeRenderer = renderer.nativePointer()
		return self._setCurrentNativeRenderer( nativeRenderer )
	
	def setCustomProperty( self, key, value ):
		"""
			\remarks	set the custom property value for the inputed key in this scene to the given value
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		return self._setNativeCustomProperty( key, self._toNativeValue(value) )
	
	def setProperty( self, key, value ):
		"""
			\remarks	[abstract]	sets the global scene property to the inputed value
			\param		key			<str> || <QString>
			\param		value		<variant>
			\return		<bool>
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setPropSetOverride( self, objects, propSet ):
		"""
			\remarks	set the override property set for the inputed objects to the given propset
			\param		objects		<list> [ <blur3d.api.SceneObject> object, .. ]
			\param		propSet		<blur3d.api.ScenePropSet>
			\return		<bool> success
		"""
		nativePropSet = None
		if ( propSet ):
			nativePropSet = propSet.nativePointer()
		
		return self._setNativePropSetOverride( self, [ obj.nativePointer() for obj in objects ], nativePropSet )
	
	def setMaterialOverride( self, objects, material, options = None ):
		"""
			\remarks	set the override material for the inputed objects to the given material
			\param		objects		<list> [ <blur3d.api.SceneObject> object, .. ]
			\param		material	<blur3d.api.SceneMaterial>
			\param		options		<blur3d.constants.MaterialOverrideOptions>
		"""
		nativeMaterial = None
		if ( material ):
			nativeMaterial = material.nativePointer()
			
		return self._setNativeMaterialOverride( [ obj.nativePointer() for obj in objects ], nativeMaterial, options = options )
	
	def setSelection( self, objects ):
		"""
			\remarks	selects the inputed objects in the scene
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._setNativeSelection( [ obj.nativePointer() for obj in objects ] )
	
	def setUpdatesEnabled( self, state ):
		"""
			\remarks	turns on/off the updating flag for the scene
			\sa			_setNativeUpdatesEnabled, updatesEnabled, update
			\param		state	<bool>
			\return		<bool> whehter or not updates are enabled
		"""
		if ( state ):
			# dequeue an update call
			self._updatesDisabled -= 1
			
			# if the updates have been fully dequeued
			if ( not self._updatesDisabled ):
				self._setNativeUpdatesEnabled( True )
		else:
			# if the scene is still able to update
			if ( not self._updatesDisabled ):
				self._setNativeUpdatesEnabled( False )
				
			self._updatesDisabled += 1
		
		return self.updatesEnabled()
		
	def softwareId( self ):
		"""
			\remarks	[abstract]	returns a unique version/bits string information that will represent the exact
									version of the software being run.
			\return		<str>
		"""
		return ''
	
	def toggleVisibleState( self, objects = None, options = None ):
		"""
			\remarks	toggle the visible options for the inputed objects
			\param		objects		<list> [ <blur3d.api.SceneObject> object, .. ]
			\param		options		<blur3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		nativeObjects = None
		if ( objects != None ):
			nativeObjects = [ obj.nativePointer() for obj in objects ]
			
		return self._toggleNativeVisibleState( nativeObjects, options )
	
	def update( self ):
		"""
			\remarks	refreshes the current scene based on the updates enabled flag
			\sa			_nativeRefresh
			\return		<bool> success
		"""
		if ( self.updatesEnabled() ):
			return self._nativeRefresh()
		return False
		
	def updatesEnabled( self ):
		"""
			\remarks	returns whether or not the scene has updates enabled
			\return		<bool> state
		"""
		return self._updatesDisabled == 0
	
	def uniqueLayerName( self, basename ):
		"""
			\remarks	returns a unique name for a layer in this scene based on the inputed base layer name
			\param		basename	<str>
			\return		<str> unique name
		"""
		names 	= [ str(layer.layerName()) for layer in self.layers() ]
		index 	= 2
		name 	= basename
		while ( name in names ):
			name = '%s%02i' % (basename,index)
			index += 1
		return name
	
	def visibleObjects( self ):
		"""
			\remarks	returns the objects that are currently visible in the scene
			\return		<list> [ <blur3d.api.SceneObject>, .. ]
		"""
		from blur3d.api import SceneObject
		return [ SceneObject( self, nativeObject ) for nativeObject in self._visibleNativeObjects() ]
	
	def worldLayer( self ):
		"""
			\remarks	[virtual]	returns the base world layer for the scene
			\return		<blur3d.api.SceneLayer> || None
		"""
		lay = self._nativeWorldLayer()
		if ( lay ):
			from blur3d.api import SceneLayer
			return SceneLayer( self, lay )
		return None
	
	@staticmethod
	def instance():
		if ( not AbstractScene._instance ):
			from blur3d.api import Scene
			AbstractScene._instance = Scene()
		return AbstractScene._instance
	
	@staticmethod
	def clearInstance():
		AbstractScene._instance = None
	
# register the symbol
from blur3d import api
api.registerSymbol( 'Scene', AbstractScene, ifNotFound = True )

# connect the clear instance method to when a scene is invalidated
import blurdev
blurdev.core.sceneInvalidated.connect( AbstractScene.clearInstance )