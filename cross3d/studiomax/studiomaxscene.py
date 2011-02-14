##
#	\namespace	blur3d.api.studiomax.studiomaxscene
#
#	\remarks	The StudiomaxScene class will define all the operations for Studiomax scene interaction.  
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blurdev import debug
from Py3dsMax 								import mxs
from blur3d.api.abstract.abstractscene 	import AbstractScene

# register custom attriutes for MAXScript that hold scene persistent data
from mxscustattribdef import MXSCustAttribDef

#-----------------------------------------------------------------------------

class EnvironmentMapHolder( MXSCustAttribDef ):
	@classmethod
	def define( cls ):
		cls.setAttrName( 'OnionMapHolder' )
		cls.defineParam( 'environmentMap', 		'textureMap',	paramId = 'eMap' )

EnvironmentMapHolder.register()

#-----------------------------------------------------------------------------

class EnvironmentMapsHolder( MXSCustAttribDef ):
	def init( self ):
		MXSCustAttribDef.init( self )
		self.setValue( 'environmentMaps', [] )
		
	@classmethod
	def define( cls ):
		cls.setAttrName( 'OnionAltMapsHolder' )
		cls.defineParam( 'environmentMaps',		'textureMapTab',	paramId = 'aMps' )
		cls.defineParam( 'currentIndex',		'integer',			paramId = 'mi' )

EnvironmentMapsHolder.register()

#-----------------------------------------------------------------------------

class CustomProperties( MXSCustAttribDef ):
	def init( self ):
		MXSCustAttribDef.init( self )
		self.setValue( 'keys', [] )
		self.setValue( 'values', [] )
		
	@classmethod
	def define( cls ):
		cls.setAttrName( 'BlurCustomProperties' )
		cls.defineParam( 'keys', 'stringTab' )
		cls.defineParam( 'values', 'stringTab' )

CustomProperties.register()
		
#-----------------------------------------------------------------------------

class SceneMetaData( MXSCustAttribDef ):
	version 	= 1.63
	
	def __init__( self, mxsInstance ):
		MXSCustAttribDef.__init__( self, mxsInstance )
		
		self._mapsHolder 		= None
		self._mapHolder 		= None
		self._custProperties 	= None
	
	def customProperties( self ):
		# pull the custom properties value
		if ( not self._custProperties ):
			root = mxs.rootNode
			data = CustomProperties.find(root)
			if ( not data ):	
				data = CustomProperties.createUnique(root)
			self._custProperties = data
		
		return self._custProperties
	
	def environmentMapCache( self ):
		# pull the map holder value
		if ( not self._mapHolder ):
			root = mxs.rootNode
			data = EnvironmentMapHolder.find( root )
			if ( not data ):
				data = EnvironmentMapHolder.createUnique( root )
			self._mapHolder = data
			
		return self._mapHolder
	
	def environmentMapsCache( self ):
		# pull the map holder value
		if ( not self._mapsHolder ):
			root = mxs.rootNode
			data = EnvironmentMapsHolder.find( root )
			if ( not data ):
				data = EnvironmentMapsHolder.createUnique( root )
			self._mapsHolder = data
			
		return self._mapsHolder
	
	def init( self ):
		MXSCustAttribDef.init( self )
		
		self.setValue( 'version', SceneMetaData.version )
		self.setValue( 'layerGroupNames', [ 'Main' ] )
		self.setValue( 'layerGroupStates', [ True ] )
		
	@classmethod
	def define( cls ):
		cls.setAttrName( 'OnionData' )
		
		# define overall parameters
		cls.defineParam( 'version', 				'float', 		paramId = 'v' )
		
		# define layer groups
		cls.defineParam( 'layerGroupNames', 		'stringTab', 	paramId = 'gn' )
		cls.defineParam( 'layerGroupStates', 		'boolTab',		paramId = 'go' )
		
		# define the scene material override list
		cls.defineParam( 'materialLibraryList',		'materialTab',	paramId = 'mtl' )
		
		# define the material cache
		cls.defineParam( 'baseMaterialCache',		'materialTab',	paramId = 'ms' )

SceneMetaData.register()

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxScene( AbstractScene ):
	def __init__( self ):
		AbstractScene.__init__( self )
		
		# create custom properties
		self._metaData 			= None
		self._mapCache			= None
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _cacheNativeMaterial( self, cacheType, nativeMaterial ):
		"""
			\remarks	implements the AbstractScene._cacheNativeMaterial method to cache the inputed material in the scene
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\param		nativeMaterial	<Py3dsMax.mxs.Material>
			\return		<bool> changed
		"""
		from blur3d.constants import MaterialCacheType
		
		# cache alternate materials
		if ( cacheType == MaterialCacheType.BaseMaterial ):
			data 	= self.metaData()
			cache 	= list(data.value( 'baseMaterialCache', [] ))
			
			# record the scene data
			if ( nativeMaterial and not nativeMaterial in cache ):
				cache.append( nativeMaterial )
				data.setValue( 'baseMaterialCache', cache )
				return True
				
		return False
	
	def _cachedNativeMaterial( self, cacheType, materialId, default = None ):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaterial method to return the cached material for the inputed material id
			\param		cacheType		<blur3d.constants.MaterialCacheType>
			\param		materialId		<str>
			\param		default			<variant>	value to return if the id was not found
			\return		<Py3dsMax.mxs.Material> nativeMaterial
		"""			
		unique_id 	= mxs.blurUtil.uniqueId
		cache 		= self._cachedNativeMaterials( cacheType )
		
		for mtl in cache:
			if ( mtl == None ):
				continue
			
			uid = str(unique_id(mtl))
			unm = str(mtl.name)
			
			if ( materialId == uid or materialId == unm ):
				return mtl
		return None
			
	def _cachedNativeMaterials( self, cacheType ):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaterials method to return the cached material for the inputed material cache type
			\param		cacheType	<blur3d.constants.MaterialCacheType>
			\return		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
		"""
		from blur3d.constants import MaterialCacheType
		
		# return override material list
		if ( cacheType == MaterialCacheType.MaterialOverrideList ):
			return self.metaData().value( 'materialLibraryList' )
		
		# return alternate material cache
		if ( cacheType == MaterialCacheType.BaseMaterial ):
			return self.metaData().value( 'baseMaterialCache' )
		
		return []
	
	def _cacheNativeMap( self, cacheType, nativeMap ):
		"""
			\remarks	implements the AbstractScene._cacheNativeMap method to cache the inputed map in the scene
			\param		cacheType	<blur3d.constants.MapCacheType>
			\param		nativeMap	<Py3dsMax.mxs.TextureMap>
			\return		<bool> changed
		"""
		from blur3d.constants import MapCacheType
		
		# return alternate environment map caches
		if ( cacheType == MapCacheType.EnvironmentMap ):
			data 	= self.metaData().environmentMapsCache()
			maps	= list(data.value('environmentMaps'))
			maps.append( nativeMap )
			data.setValue( 'environmentMaps', maps )
			
		return False
		
	def _cachedNativeMap( self, cacheType, mapId, default = None ):
		"""
			\remarks	implements the AbstractScene._cachedNativeMap method to return the cached map for the inputed map id
			\param		cacheType		<blur3d.constants.MapCacheType>
			\param		mapId			<str>
			\param		default			<variant>	value to return if the id was not found
			\return		<Py3dsMax.mxs.TextureMap> nativeMap
		"""			
		unique_id 	= mxs.blurUtil.uniqueId
		cache 		= self._cachedNativeMaps( cacheType )
		
		for nativeMap in cache:
			if ( nativeMap == None ):
				continue
			
			uid = str(unique_id(nativeMap))
			unm = str(nativeMap.name)
			
			if ( mapId == uid or mapId == unm ):
				return nativeMap
		return None
		
	def _cachedNativeMaps( self, cacheType ):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaps method to return the cached maps for the given type from the scene
			\param		cacheType		<blur3d.constants.MapCacheType>
			\return		<list> [ <Py3dsMax.mxs.TextureMap> nativeMap, .. ]
		"""
		from blur3d.constants import MapCacheType
		
		# return alternate environment map caches
		if ( cacheType == MapCacheType.EnvironmentMap ):
			data = self.metaData().environmentMapsCache()
			return data.value( 'environmentMaps' )
		
		return []
		
	def _clearNativeMaterialOverride( self, nativeObjects ):
		"""
			\remarks	implements AbstractScene._clearNativeMaterialOverride method to clear the native override materials from the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		from blur3d.constants 			import MaterialCacheType
		from blur3d.api.studiomax 	import StudiomaxAppData
		
		# store the methods we're going to use
		get_userprop 	= mxs.getUserProp
		set_userprop	= mxs.setUserProp
		get_appdata		= mxs.getAppData
		del_appdata		= mxs.deleteAppData
		superclassof	= mxs.superClassOf
		geoclass		= mxs.GeometryClass
		
		for obj in nativeObjects:
			# ignore non-geometric objects
			if ( not superclassof(obj) == geoclass ):
				continue
				
			# pull the app data
			mid = get_appdata( obj, StudiomaxAppData.AltMtlIndex )
			
			# pull the user properties
			if ( mid == None ):
				mid = get_userprop( obj, 'basematerial' )
			
			# record the base material if it is not already recorded
			if ( mid and mid != 'undefined' ):
				# clear the cache data
				del_appdata( obj, StudiomaxAppData.AltMtlIndex )
				set_userprop( obj, 'basematerial', 'undefined' )
				
				# restore the original material
				if ( mid == '0' ):
					obj.material = None
				else:
					obj.material = self._cachedNativeMaterial( MaterialCacheType.BaseMaterial, mid )
		
		return True
	
	def _clearNativePropSetOverride( self, nativeObjects ):
		"""
			\remarks	implements the AbstractScene._clearNativePropSetOverride method to clear the inputed objects of any overriding property set information
			\param		nativeObjects		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		# store the methods we're going to use
		from blur3d.api 			import SceneObjectPropSet
		from blur3d.api.studiomax 	import StudiomaxAppData
		
		get_appdata		= mxs.getAppData
		del_appdata		= mxs.deleteAppData
		get_userprop 	= mxs.getUserProp
		set_userprop	= mxs.setUserProp
		altpropindex	= StudiomaxAppData.AltPropIndex
		
		for obj in nativeObjects:
			# restore base properties
			props = get_appdata( obj, altpropindex )
			if ( not props ):
				props = get_userprop( obj, 'baseprops' )
			
			# restore the property set
			if ( props and props != 'undefined' ):
				nprop = SceneObjectPropSet( self, None )
				nprop._setValueString( props )
				for key in nprop.propertyNames():
					if ( nprop.isCustomProperty( key ) ):
						set_userprop( obj, key, str(self._toNativeValue(nprop.value(key))) )
					else:
						obj.setProperty( key, self._toNativeValue(nprop.value(key)) )
						
				# if this propset is empty, this is all we need to do
				set_userprop( obj, 'baseprops', 'undefined' )
				del_appdata( obj, altpropindex )
		
		return True
	
	def _createNativeLayer( self, name, nativeObjects = [] ):
		"""
			\remarks	implements the AbstractScene._createNativeLayer method to return a new Studiomax layer
			\param		name			<str>
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		lay = mxs.layerManager.newLayerFromName( str(name) )
		if ( lay ):
			addnode = lay.addNode
			for obj in nativeObjects:
				addnode( obj )
		return lay
		
	def _createNativeLayerGroup( self, name, nativeLayers = [] ):
		"""
			\remarks	implements the AbstractScene._createNativeLayerGroup method to create a new layer group in this scene based on the inputed name with the given layers
			\param		name			<str>
			\return		<str> nativeLayerGroup || None
		"""
		names 	= list(self.metaData().value( 'layerGroupNames' ))
		states 	= list(self.metaData().value( 'layerGroupStates' ))
		if ( not name in names ):
			names.append( str(name) )
			states.append( True )
			self.metaData().setValue( 'layerGroupNames', names )
			self.metaData().setValue( 'layerGroupStates', states )
			return name
		return ''
		
	def _createNativeModel( self, name = 'New Model', nativeObjects = [] ):
		"""
			\remarks	implements the AbstractScene._createNativeModel method to return a new Studiomax model
			\param		name			<str>
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		output = mxs.Point( name = name )
		if ( nativeObjects ):
			output.parent = nativeObjects[0].parent
			for nativeObject in nativeObjects:
				nativeObject.parent = output
		return output
	
	def _createNativeRenderer( self, rendererType ):
		"""
			\remaks		implements AbstractScene._createNativeRenderer to create a new renderer based on the inputed rendererType for this scene
			\param		rendererType		<blur3d.constants.RendererType>
			\return		<Py3dsMax.mxs.Renderer> nativeRenderer || None
		"""
		from blur3d.constants import RendererType
		
		# create a scanline renderer
		if ( rendererType == RendererType.Scanline ):
			return mxs.Default_Scanline_Renderer()
		
		# create a Mental Ray renderer
		elif ( rendererType == RendererType.MentalRay ):
			return mxs.mental_ray_renderer()
		
		# create a VRay renderer
		elif ( rendererType == RendererType.VRay ):
			renderers = mxs.rendererClass.classes
			
			# find the installed V_Ray renderer
			for renderer in renderers:
				clsname = str(renderer)
				if ( not clsname.startswith( 'V_Ray_RT' ) and clsname.startswith( 'V_Ray_' ) ):
					return renderer()
		
		# create a specific renderer
		else:
			renderers = mxs.rendererClass.classes
			
			# find the installed V_Ray renderer
			for renderer in renderers:
				clsname = str(renderer)
				if ( clsname == rendererType ):
					return renderer()
					
		return None
	
	def _currentNativeRenderer( self ):
		"""
			\remarks	implements AbstractScene._currentNativeRenderer method to return the current native renderer for this scene instance
			\return		<Py3dsMax.mxs.Renderer> nativeRenderer || None
		"""
		return mxs.renderers.current
	
	def _exportNativeObjects( self, objects, filename = '' ):
		"""
			\remarks	implements the AbstractScene._exportNativeObjects method to save out individual objects to a file
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		filename		<str>
			\return		<bool> success
		"""
		return mxs.saveNodes( objects, filename )
	
	def _findNativeObject( self, objectName = '', objectId = 0 ):
		"""
			\remarks	implements the AbstractScene._findNativeObject to look up an object based on the inputed name
			\sa			findNativeObject
			\param		objectName	<str>
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		objectName 	= str(objectName)
		output 		= None
		if ( objectName ):
			output = mxs.getNogyName( str(objectName) )
		
		if ( not output and objectId ):
			output = mxs.refByUniqueId( objectId )
		
		return output
		
	def _findNativeLayer( self, layerName = '', layerId = 0 ):
		"""
			\remarks	implements the AbstractScene._findNativeLayer to look up a layer based on the inputed name
			\sa			findNativeLayer
			\param		layerName	<str>
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		if ( layerName == 'World Layer' ):
			layerName = '0'
		
		output = None
		if ( layerName ):
			output = mxs.layerManager.getLayerFromName( str(layerName) )
		
		if ( not output and layerId ):
			output = mxs.layerManager.refByUniqueId( layerId )
			
		return output
		
	def _findNativeLayerGroup( self, groupName = '', groupId = 0 ):
		"""
			\remarks	implements the AbstractScene._findNativeLayerGroup to look up a layer group based on the inputed name
			\sa			findNativeLayer
			\param		layerName	<str>
			\return		<str> nativeLayerGroup || None
		"""
		names 		= list(self.metaData().value('layerGroupNames'))
		groupName 	= str(groupName)
		if ( groupName in names ):
			return groupName
		return None
	
	def _findNativeMaterial( self, materialName = '', materialId = 0 ):
		"""
			\remarks	implements the AbstractScene._findNativeMaterial to look up an material based on the inputed name
			\sa			findNativeMaterial
			\param		materialName	<str>
			\return		<Py3dsMax.mxs.Material> nativeMaterial || None
		"""
		materialName 	= str(materialName)
		if ( not (materialName or materialId) ):
			return None
		
		uniqueid = mxs.blurUtil.uniqueId
		for material in self._nativeMaterials():
			if ( material.name == materialName or uniqueid(material) == materialId ):
				return material
		
		debug.debugObject( self._findNativeMaterial, 'could not find material (%s - %s)' % (materialName,materialId) )
				
		return None
		
	def _findNativeMap( self, mapName = '', mapId = 0 ):
		"""
			\remarks	implements the AbstractScene._findNativeMap to look up an map based on the inputed name
			\sa			findNativeMap
			\param		mapName	<str>
			\return		<Py3dsMax.mxs.Map> nativeMap || None
		"""
		mapName 	= str(mapName)
		
		if ( not (mapName or mapId) ):
			return None
		
		uniqueid = mxs.blurUtil.uniqueId
		for nmap in self._collectNativeMaps():
			if ( nmap.name == mapName or uniqueid(nmap) == mapId ):
				return nmap
				
		return None
		
	def _freezeNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	implements the AbstractScene._freezeNativeObjects method to freeze(lock)/unfreeze(unlock) the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		if ( state ):
			mxs.freeze( nativeObjects )
		else:
			mxs.unfreeze( nativeObjects )
	
	def _hideNativeObjects( self, nativeObjects, state ):
		"""
			\remarks	implements the AbstractScene._hideNativeObjects method to hide/unhide the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		if ( state ):
			mxs.hide( nativeObjects )
		else:
			mxs.unhide( nativeObjects )
	
	def _fromNativeValue( self, nativeValue ):
		"""
			\remarks	re-implements the AbstractScene._fromNativeValue method to convert
						some native maxscript values to proper python/pyqt values
			\param		nativeValue		<variant>
			\return		<variant>
		"""
		classof = mxs.classof
		cls		= classof( nativeValue )
		
		# return the value as a QColor
		if ( cls == mxs.Color ):
			from PyQt4.QtGui import QColor
			return QColor( nativeValue.r, nativeValue.g, nativeValue.b )
		
		# convert value from a Time
		if ( cls == mxs.Time ):
			return int(nativeValue)
		
		# convert from name to a String
		if ( cls == mxs.Name ):
			return str(nativeValue)
		
		# return the standard value
		return AbstractScene._fromNativeValue( self, nativeValue )
	
	def _getNativeObject( self ):
		"""
			\remarks	[abstract]	invokes the application's ability to let a user select a Object from the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.selectByName( single = True )
	
	def _getNativeMaterial( self ):
		"""
			\remarks	implements the AbstractScene._getNativeMaterial method to invoke the application's ability to let a user select a Material from the scene
			\return		<Py3dsMax.mxs.Material> nativeMaterial || None
		"""
		return mxs.materialBrowseDlg( mxs.pyhelper.namify( "mats" ) )
	
	def _getNativeMap( self ):
		"""
			\remarks	implements the AbstractScene._getNativeMap method to invoke the application's ability to let a user select a Map from the scene
			\return		<Py3dsMax.mxs.TextureMap> nativeMap || None
		"""
		return mxs.materialBrowseDlg( mxs.pyhelper.namify( "maps" ) )
	
	def _loadNativeMaterialsFromLibrary( self, filename = '' ):
		"""
			\remarks	[abstract] loads a bunch of materials from the inputed library location, or prompts the user to select a library when not provided
			\param		filename	<str>
			\return		<list> [ <Py3dsMax.mxs.TextureMap> nativeMaterial, .. ]
		"""
		from PyQt4.QtGui import QFileDialog
		filename = QFileDialog.getOpenFileName( None, 'Load Material Library', '', 'Material Library files (*.mat)' )
		if ( filename ):
			is_kindof	= mxs.isKindOf
			TextureMap	= mxs.TextureMap
			mlib 		= mxs.loadTempMaterialLibrary( str(filename) )
			output 		= [ mtl for mtl in mlib if not is_kindof( mtl, TextureMap ) ]
			
			# clear the material library - this is a memory intensive section
			del mlib
			mxs.gc()
			
			return output
		return []
	
	def _nativeActiveLayer( self ):
		"""
			\remarks	implements the AbstractScene._nativeActiveLayer method to return the native active layer from the scene
			\param		name			<str>
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		return mxs.layerManager.current
	
	def _nativeAtmospherics( self ):
		"""
			\remarks	implements the AbstractScene._nativeAtmospherics method to return a list of the atmospheric instances in this scene
			\return		<list> [ <Py3dsMax.mxs.Atmospheric> nativeAtmospheric, .. ]
		"""
		get_atmos 	= mxs.getAtmospheric
		get_effect 	= mxs.getEffect
		return [ get_atmos( i+1 ) for i in range( mxs.numAtmospherics ) ] + [ get_effect( i + 1 ) for i in range( mxs.numEffects ) ]
	
	def _nativeCameras( self ):
		"""
			\remarks	implements the AbstractScene._nativeCameras method to return a list of the camera instances in this scene
			\return		<list> [ <Py3dsMax.mxs.Camera> nativeCamera, .. ]
		"""
		return mxs.cameras
	
	def _nativeCustomProperty( self, key, default = None ):
		"""
			\remarks	implements the AbstractScene._nativeCustomProperty method to return a value for the inputed key for a custom scene property
			\param		key		<str>
			\param		default	<variant>
			\return		<variant>
		"""
		key		= str(key)
		props 	= self.metaData().customProperties()
		keys	= list(props.value('keys'))
		if ( key in keys ):
			values	= list(props.value('values'))
			return values[keys.index(key)]
		return default
	
	def _nativeEnvironmentMap( self ):
		"""
			\remarks	implements the AbstractScene._nativeEnvironmentMap method to return the native map for the environment of this scene
			\return		<Py3dsMax.mxs.TextureMap> nativeMap || None
		"""
		return mxs.environmentMap
	
	def _nativeEnvironmentMapOverride( self ):
		"""
			\remarks	implements the AbstractScene._nativeEnvironmentMapOverride method to return the native map for the environment of this scene
			\return		<Py3dsMax.mxs.TextureMap> nativeMap || None
		"""
		data = self.metaData().environmentMapsCache()
		index = data.value( 'currentIndex' )
		if ( index ):
			maps = list(data.value('environmentMaps'))
			return maps[index-1]
		return None
	
	def _nativeLayers( self ):
		"""
			\remarks	implements the AbstractScene._nativeLayers method to return a list of the native layers in this scene
			\return		<list> [ <Py3dsMax.mxs.Layer> nativeLayer, .. ]
		"""
		layerManager 	= mxs.layerManager
		count 			= layerManager.count
		getLayer 		= layerManager.getLayer
		return [ getLayer(i) for i in range(count) ]
	
	def _nativeLayerGroups( self ):
		"""
			\remarks	implements the AbstractScene._nativeLayerGroups method to return a list of the native layer groups in this scene
			\return		<list> [ <str> nativeLayerGroup, .. ]
		"""
		return self.metaData().value( 'layerGroupNames' )
	
	def _nativeMaterials( self ):
		#get_instances	= mxs.getClassInstances
		#mclasses 		= mxs.Material.classes
		#output			= []
		
		# collect all the materials
		#for mclass in mclasses:
		#	output += get_instances(mclass)
		output = list(mxs.sceneMaterials)
			
		# include material list
		mlist = list(self.metaData().value( 'materialLibraryList' ))
		for m in mlist:
			if ( m and not m in output ):
				output.append(m)
				
		# include material cache
		mcache = list(self.metaData().value( 'baseMaterialCache' ))
		for m in mcache:
			if ( m and not m in output ):
				output.append(m)
		
		# include layer materials
		for layer in self.layers():
			for m in layer._nativeAltMaterials():
				if ( m and not m in output ):
					output.append(m)
		
		# define the material cache
		return output
	
	def _nativeMaps( self ):
		get_instances	= mxs.getClassInstances
		output			= get_instances(mxs.BitmapTexture)
		
		# include material list
		mlist = list(self.metaData().environmentMapsCache().value( 'environmentMaps' ))
		for m in mlist:
			if ( m and not m in output ):
				output.append(m)
				
		return output
		
	def _nativeObjects( self ):
		"""
			\remarks	implements the AbstractScene._nativeObjects method to return the native objects from the scene
			\return		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
		"""
		return mxs.objects
	
	def _nativeRefresh( self ):
		"""
			\remarks	implements the AbstractScene._nativeRefresh method to refreshe the contents of the current scene
			\sa			setUpdatesEnabled, update
			\return		<bool> success
		"""
		if ( not mxs.isSceneRedrawDisabled() ):
			mxs.redrawViews()
			return True
		return False
	
	def _nativeRootObject( self ):
		"""
			\remarks	implements the AbstractScene._nativeRootObject to return the native root object of the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.rootNode
	
	def _nativeSelection( self ):
		"""
			\remarks	implements the AbstractScene._nativeSelection to return the native selected objects of the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.selection
	
	def _nativeToggleVisibleOptions( self, nativeObjects = None, options = None ):
		"""
			\remarks	implements the AbstractScene.toggleVisibleOptions method to toggle the visible state of the inputed options for the given objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		options			<blur3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		from blur3d.api.studiomax 	import cachelib
		from blur3d.constants 		import VisibilityToggleOptions
		from Py3dsMax 				import mxs
		from blur3d.api.studiomax 	import cachelib
		
		# toggle all the visibility options by default
		if ( options == None ):
			options = VisibilityToggleOptions.All
	
		if ( not options ):
			return False
			
		if ( nativeObjects == None ):
			nativeObjects = mxs.objects
	
		# store maxscript values
		superclassof		= mxs.superClassOf
		classof				= mxs.classof
		B2_Main_Light		= mxs.B2_Main_Light
		VRaySun				= mxs.VraySun
		VRayIES				= mxs.VRayIES
		VRayAmbientLight	= mxs.VRayAmbientLight
		Light_Portal		= mxs.Light_Portal
		XRefObject			= mxs.XRefObject
		Missing_Light		= mxs.Missing_Light
		Light				= mxs.Light
		Event				= mxs.Event
		FumeFX				= mxs.FumeFX
		PF_Source			= mxs.PF_Source
		
		for obj in nativeObjects:
			state 	= not obj.ishidden
			msuper	= superclassof( obj )
			mcls 	= classof( obj )
			
			# toggle lights
			if ( options & VisibilityToggleOptions.ToggleLights ):
				if ( msuper == Light ):
					# update a brazil 2 light
					if ( mcls == B2_Main_Light ):
						obj.base_parameters.enabled_on = state
					
					# update vray lights
					elif ( mcls in (VRaySun,VRayIES,VRayAmbientLight) ):
						obj.enabled = state
					
					# update a light portal
					elif ( mcls == Light_Portal ):
						obj.portal_on = state
						obj.renderable = state
					
					# update an xref object
					elif ( mcls == XRefObject ):
						obj.actualBaseObject.on = state
						obj.renderable = state
					
					# update a missing light
					elif ( mcls == Missing_Light ):
						print 'Warning: Missing Lights found in the Scene'
				
					# update a default light
					else:
						obj.renderable 	= state
						obj.on 			= state
					
					# don't bother processing future checks if this was a light
					continue
					
			# toggle fx
			if ( options & VisibilityToggleOptions.ToggleFX ):
				# update an event
				if ( mcls == Event ):
					if ( obj.layer.name != '0' ):
						obj.activate( state )
					continue
				
				# update a fume effect
				elif ( mcls == FumeFX ):
					obj.renderable = state
					continue
				
				# update a particle flow source
				elif ( mcls == PF_Source ):
					obj.enable_particles = state
					obj.baseObject.activateParticles( state )
					continue
		
			if ( options & VisibilityToggleOptions.ToggleCaches ):
				cachelib.toggleCaches( obj, state )
					
		return True
		
	def _nativeWorldLayer( self ):
		"""
			\remarks	implements the AbstractScene._nativeWorldLayer to return the native world layer of the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.layerManager.getLayer(0)
	
	def _removeNativeObjects( self, nativeObjects ):
		"""
			\remarks	implements the AbstractScene._removeNativeObjects to remove the inputed objects from the scene
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		mxs.delete( nativeObjects )
		return True
	
	def _renameNativeObjects( self, nativeObjects, names, display = True ):
		"""
			\remarks	implements the AbstractScene._renameNativeObjects to rename the inputed objects from the scene
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		names			<list> [ <str> name, .. ]
			\param		display			<bool> 	tags whether or not the names are display names or object names
			\return		<bool> success
		"""
		# make sure we have the proper number of names and objects
		if ( len( names ) != len( nativeObjects ) ):
			return False
		
		# keep the model names when changing display only
		if ( display ):
			for i, obj in enumerate(nativeObjects):
				n = obj.name
				if ( '.' in n ):
					splt 			= n.split( '.' )
					splt[-1] 		= names[i]
					names[i] = '.'.join( splt )
		
		# set the names
		mxs.blurUtil.setNames( nativeObjects, names )
		return True
	
	def _setCachedNativeMaps( self, cacheType, nativeMaps ):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaps method to set the cached maps for the given type from the scene
			\param		cacheType		<blur3d.constants.MapCacheType>
			\param		nativeMaps		<list> [ <Py3dsMax.mxs.TextureMap> nativeMap, .. ]
			\return		<bool> success
		"""
		from blur3d.constants import MapCacheType
		
		# return alternate environment map caches
		if ( cacheType == MapCacheType.EnvironmentMap ):
			data.setValue( 'environmentMaps', nativeMaps )
			return True
		
		return True
	
	def _setCachedNativeMaterials( self, cacheType, nativeMaterials ):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaterials method to set the cached materials for the given type from the scene
			\param		cacheType			<blur3d.constants.MaterialCacheType>
			\param		nativeMaterials		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
			\return		<bool> success
		"""
		from blur3d.constants import MaterialCacheType
		
		# return override material list
		if ( cacheType == MaterialCacheType.MaterialOverrideList ):
			self.metaData().setValue( 'materialLibraryList', nativeMaterials )
			return True
		
		# return alternate material cache
		if ( cacheType == MaterialCacheType.BaseMaterial ):
			self.metaData().setValue( 'baseMaterialCache', nativeMaterials )
			return True
		
		return False
	
	def _setCurrentNativeRenderer( self, nativeRenderer ):
		"""
			\remarks	implements the AbstractScene._setCurrentNativeRenderer method to set the current renderer to the inputed native renderer
			\param		nativeRenderer	<variant>
			\return		<bool> success
		"""
		mxs.pyhelper.setCurrentRenderer( nativeRenderer )
		return True
	
	def _setNativeCustomProperty( self, key, value ):
		"""
			\remarks	implements the AbstractScene._nativeCustomProperty method to set a value for the inputed key for a custom scene property
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		key		= str(key)
		value	= str(value)
		props 	= self.metaData().customProperties()
		keys	= list(props.value('keys'))
		values	= list(props.value('values'))
		
		# replace an existing property
		if ( key in keys ):
			values[keys.index(key)] = value
		
		# set a new property
		else:
			keys.append(key)
			values.append(value)
		
		props.setValue( 'keys', 	keys )
		props.setValue( 'values', 	values )
		
		return True
	
	def _setNativeEnvironmentMap( self, nativeMap ):
		"""
			\remarks	implements the AbstractScene._setNativeEnvironmentMap method to set the environment map for this scene
			\param		nativeMap 	<Py3dsMax.mxs.Material> || None
			\return		<bool> success
		"""
		mxs.environmentMap = nativeMap
		return True
	
	def _setNativeEnvironmentMapOverride( self, nativeMap ):
		"""
			\remarks	implements the AbstractScene._setNativeEnvironmentMapOverride method to set the environment map override for this scene
			\param		nativeMap 	<Py3dsMax.mxs.TextureMap> || None
			\return		<bool> success
		"""
		data 		= self.metaData().environmentMapsCache()
		basedata 	= self.metaData().environmentMapCache()
		
		# if we are going into an override state
		if ( nativeMap ):
			# record the current map to the backup cache
			if ( data.value( 'currentIndex' ) == 0 ):
				basedata.setValue( 'environmentMap', mxs.environmentMap )
			
			# make sure the map is cached as an override option
			maps = list(data.value( 'environmentMaps' ))
			if ( not nativeMap in maps ):
				maps.append( nativeMap )
				data.setValue( 'environmentMaps', nativeMap )
			
			# set the override in the system
			data.setValue( 'currentIndex', maps.index(nativeMap) + 1 )
			mxs.environmentMap = nativeMap
			return True
			
		# otherwise, restore the base state
		else:
			mxs.environmentMap = basedata.value( 'environmentMap' )
			basedata.setValue( 'environmentMap', None )
			data.setValue( 'currentIndex', 0 )
			return True
	
	def _setNativePropSetOverride( self, nativeObjects, nativePropSet ):
		"""
			\remarks	implements the AbstractScene._setNativePropSetOverride method to set the inputed objects with an overriding property set
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		nativePropSet	<blur3d.api.SceneObjectPropSet>
			\return		<bool> success
		"""
		from blur3d.api 			import SceneObjectPropSet
		from blur3d.api.studiomax 	import StudiomaxAppData
		
		get_appdata		= mxs.getAppData
		del_appdata		= mxs.deleteAppData
		set_appdata		= mxs.setAppData
		get_prop		= mxs.getProperty
		set_prop		= mxs.setProperty
		get_userprop 	= mxs.getUserProp
		set_userprop	= mxs.setUserProp
		altpropindex	= StudiomaxAppData.AltPropIndex
		empty 			= not nativePropSet.isActive()
		values 			= [ (key,nativePropSet.value(key),nativePropSet.isCustomProperty(key)) for key in nativePropSet.activeProperties() ]
		
		for obj in nativeObjects:
			# restore base properties
			props = get_appdata( obj, altpropindex )
			if ( not props ):
				props = get_userprop( obj, 'baseprops' )
			
			# restore the property set
			if ( props and props != 'undefined' ):
				nprop = SceneObjectPropSet( self, None )
				nprop._setValueString( props )
				for key in nprop.propertyNames():
					if ( nprop.isCustomProperty( key ) ):
						set_userprop( obj, key, str(self._toNativeValue(nprop.value(key))) )
					else:
						obj.setProperty( key, self._toNativeValue(nprop.value(key)) )
						
				# if this propset is empty, this is all we need to do
				if ( empty ):
					set_userprop( obj, 'baseprops', 'undefined' )
					del_appdata( obj, altpropindex )
					continue
			
			# record the base state if it is not already recorded
			elif ( not empty ):
				nprop = SceneObjectPropSet( self, None )
				nprop.activateProperties(True)
				
				# go through and pull the values
				for key in nprop.propertyNames():
					if ( nprop.isCustomProperty(key) ):
						value = get_userprop( obj, key )
					else:
						value = obj.property( key )
					
					if ( value != None ):
						nprop.setValue( key, self._fromNativeValue(value) )
				
				# collect the initial base properties
				valueString = nprop._valueString()
				set_userprop( obj, 'baseprops', valueString )
				set_appdata( obj, altpropindex, valueString )
			
			# pass this object if it is null
			else:
				continue
			
			# apply this property if it is not empty
			for key, value, custom in values:
				if ( custom ):
					set_userprop( obj, key, str(self._toNativeValue(value)) )
				else:
					obj.setProperty( key, self._toNativeValue(value) )
		
		return True
	
	def _setNativeMaterialOverride( self, nativeObjects, nativeMaterial, options = None ):
		"""
			\remarks	implements AbstractScene._setNativeMaterialOverride to apply this material as an override to the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		nativeMaterial	<Py3dsMax.mxs.Material> nativeMaterial
			\param		options			<blur3d.constants.MaterialOverrideOptions>
			\return		<bool> success
		"""
		from blur3d.constants 		import MaterialOverrideOptions, MaterialCacheType
		from blur3d.api.studiomax	import matlib
		from blur3d.api.studiomax 	import StudiomaxAppData
		
		# store the methods we're going to use
		get_userprop 	= mxs.getUserProp
		set_userprop	= mxs.setUserProp
		get_appdata		= mxs.getAppData
		set_appdata		= mxs.setAppData
		superclassof	= mxs.superClassOf
		geoclass		= mxs.GeometryClass
		unique_id		= mxs.blurUtil.uniqueId
		processed		= {}
		
		for obj in nativeObjects:
			# ignore non-geometric objects
			if ( not superclassof(obj) == geoclass ):
				continue
				
			# pull the app data
			mid = get_appdata( obj, StudiomaxAppData.AltMtlIndex )
			
			# pull the user properties
			if ( mid == None ):
				mid = get_userprop( obj, 'basematerial' )
			
			# record the base material if it is not already recorded
			if ( not mid or mid == 'undefined' ):
				baseMaterial = obj.material
				
				if ( baseMaterial ):
					uid = unique_id( baseMaterial )
					set_appdata( obj, StudiomaxAppData.AltMtlIndex, str(uid) )
					set_userprop( obj, 'basematerial', str(uid) )
					self._cacheNativeMaterial( MaterialCacheType.BaseMaterial, baseMaterial )
				else:
					set_appdata( obj, StudiomaxAppData.AltMtlIndex, '0' )
					set_userprop( obj, 'basematerial', '0' )
			
			# otherwise restore the base material
			else:
				baseMaterial 	= self._cachedNativeMaterial( MaterialCacheType.BaseMaterial, mid )
			
			# assign the override for the material based on the options
			uid					= unique_id(baseMaterial)
			overrideMaterial 	= processed.get( uid )
			if ( not overrideMaterial ):
				overrideMaterial 	= matlib.createMaterialOverride( baseMaterial, nativeMaterial, options = options )
				processed[uid] 		= overrideMaterial
				
			obj.material = overrideMaterial
				
		return True
		
	def _setNativeSelection( self, selection ):
		"""
			\remarks	implements the AbstractScene._setNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		if ( not selection ):
			mxs.clearSelection()
		else:
			mxs.select( selection )
		return True
	
	def _setNativeUpdatesEnabled( self, state ):
		"""
			\remarks	[virtual] reimplements the AbstractScene._setNativeUpdatesEnabled to enable/disable scene updates
			\sa			setUpdatesEnabled
			\param		state		<bool>
			\return		<bool> success
		"""
		if ( state ):
			# disable quiet mode
			mxs.setQuietMode( False )
			
			# enable undo operations
			mxs.theHold.EnableUndo()
			
			# reset the command panel state
			mxs.setCommandPanelTaskMode( self._panelState )
			self._panelState = None
			
			# allow panel editing
			mxs.resumeEditing()
			
			# enable scene redrawing and refresh the views
			while ( mxs.isSceneRedrawDisabled() ):
				mxs.enableSceneRedraw()
				
			mxs.redrawViews()
	
		else:
			# enable quiet mode
			mxs.setQuietMode( True )
			
			# disallow panel editing
			mxs.suspendEditing()
			
			# disable the scene redrawing
			mxs.disableSceneRedraw()
			mxs.theHold.DisableUndo()
			
			# record the command panel state
			self._panelState = mxs.getCommandPanelTaskMode()
			mxs.setCommandPanelTaskMode( mxs.pyhelper.namify('create') )
	
	def _toNativeValue( self, pyValue ):
		"""
			\remarks	[virtual] reimplements the AbstractScene._setNativeUpdatesEnabled to convert the inputed value from Qt/Python to whatever value is required for the native application
			\param		pyValue	<variant>
			\return		<variant>
		"""
		from PyQt4.QtGui import QColor
		
		# convert the value from a color
		if ( isinstance( pyValue, QColor ) ):
			return mxs.Color( pyValue.red(), pyValue.green(), pyValue.blue() )
			
		# return the standard value
		return AbstractScene._toNativeValue( self, pyValue )
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def checkForSave( self ):
		"""
			\remarks	implements AbstractScene.checkForSave method to prompt the user to save and continue, returning false on a user cancel
			\return		<bool> success
		"""
		return mxs.checkForSave()
		
	def cleanMetaData( self ):
		root	= mxs.rootNode
		
		# remove undefined environment maps
		data = EnvironmentMapsHolder.find(root)
		if ( data ):
			currentIndex 	= data.value( 'currentIndex' )
			oldMaps			= list(data.value( 'environmentMaps', [] ))
			
			newMaps = []
			for i, m in enumerate(oldMaps):
				if ( m == None and i <= currentIndex ):
					currentIndex -=1
				elif ( m ):
					newMaps.append( m )
			
			data.setValue( 'currentIndex', currentIndex )
			data.setValue( 'environmentMaps', newMaps )
		
		# remove undefined layers
		count 				= mxs.custAttributes.count( root )
		getLayerFromName 	= mxs.layerManager.getLayerFromName
		get_attr 			= mxs.custAttributes.get
		rem_attr			= mxs.custAttributes.delete
		is_prop				= mxs.isproperty
		
		for i in range( count - 1, -1, -1 ):
			attr = get_attr( root, i+1 )
			if ( str(attr.name).lower() == 'oniondata' ):
				layer = None
				
				# grab the layer by its name
				if ( is_prop( attr, 'lnm' ) and attr.lnm ):
					layer = getLayerFromName( attr.lnm )
				
				# remove the layer reference
				if ( not layer ):
					rem_attr( root, i+1 )
		
	def currentFileName( self ):
		"""
			\remarks	implements AbstractScene.currentFileName method to return the current filename for the scene that is active in the application
			\return		<str>
		"""
		return mxs.maxFilePath + mxs.maxFileName
	
	def holdCurrentState( self ):
		"""
			\remarks	implements AbstractScene.holdCurrentState to protect the current scene as it is to allow for manipulation and provide a restore point
			\sa			restoreHeldState
		"""
		mxs.holdMaxFile()
	
	def fileType( self ):
		"""
			\remarks	implements AbstractScene.fileType to return the main file type for this type of application
			\return		<str>
		"""
		return '.max'
	
	def fileTypes( self ):
		"""
			\remarks	implements AbstractScene.fileTypes to return the associated file types for this type of application
			\return		<list> [ <str>, .. ]
		"""
		return [ 'Max files (*.max)' ]
	
	def loadFile( self, filename = '' ):
		"""
			\remarks	implements AbstractScene.loadFile to load the inputed filename into the application, returning true on success
			\param		filename	<str>
			\return		<bool> success
		"""
		if ( not filename ):
			from PyQt4.QtGui import QFileDialog
			filename = QFileDialog.getOpenFileName( None, 'Load Max File', '', 'Max files (*.max);;All files (*.*)' )
		
		if ( filename ):
			mxs.loadMaxFile( str( filename ) )
			return True
		return False
	
	def metaData( self ):
		"""
			\remarks	initializes the SceneMetaData class for this scene instance for retrieving information from the scene
			\return		<SceneMetaData>
		"""
		if ( not self._metaData ):
			# cleanup existing data
			self.cleanMetaData()
			
			data = SceneMetaData.find( mxs.globaltracks )
			if ( data ):
				version = round( data.value( 'version' ), 2 )
				# determine if we need to upgrade
				if ( version < SceneMetaData.version ):
					# update the data
					print 'update the data', data.value( 'version' ), SceneMetaData.version
			else:
				# create the main data
				data = SceneMetaData.createUnique( mxs.globaltracks )
			
			self._metaData = data
				
		return self._metaData
	
	def property( self, key, default = None ):
		"""
			\remarks	implements AbstractScene.property to return a global scene value
			\param		key			<str> || <QString>
			\param		default		<variant>	default value to return if no value was found
			\return		<variant>
		"""
		value = getattr( mxs, str(key) )
		if ( not value ):
			return default
		
		return self._fromNativeValue( value )
	
	def reset( self ):
		"""
			\remarks	implements AbstractScene.reset to reset this scene for all the data and in the application
			\return		<bool> success
		"""
		mxs.resetMaxFile()
		return True
		
	def restoreHeldState( self ):
		"""
			\remarks	implements AbstractScene.restoreHeldState to restore a held state after processing code
			\sa			holdCurrentState
			\return		<bool> success
		"""
		mxs.fetchMaxFile()
		
		# flush the maxscript memory that was used during the hold state
		mxs.gc()	# first time marks items ready for removal
		mxs.gc()	# second time removes items that are ready for removal
		
		return True
	
	def saveFileAs( self, filename = '' ):
		"""
			\remarks	implements AbstractScene.saveFileAs to save the current scene to the inputed name specified.  If no name is supplied, then the user should be prompted to pick a filename
			\param		filename 	<str>
			\return		<bool> success
		"""
		if ( not filename ):
			from PyQt4.QtGui import QFileDialog
			filename = QFileDialog.getSaveFileName( None, 'Save Max File', '', 'Max files (*.max);;All files (*.*)' )
		
		if ( filename ):
			mxs.saveMaxFile( str(filename) )
			return True
		return False
	
	def setLayerGroups( self, layerGroups ):
		"""
			\remarks	reimplements the AbstractScene.setLayerGroups method to set the scene layer groups to the inputed list
			\param		layerGroups		<list> [ <blur3d.api.SceneLayerGroup> layerGroup, .. ]
			\return		<bool> success
		"""
		groupNames 	= []
		groupStates = []
		
		for layerGroup in layerGroups:
			groupNames.append( str(layerGroup.groupName()) )
			groupStates.append( layerGroup.isOpen() )
		
		data = self.metaData()
		data.setValue( 'layerGroupNames', groupNames )
		data.setValue( 'layerGroupStates', groupStates )
		
		return True
	
	def setProperty( self, key, value ):
		"""
			\remarks	implements AbstractScene.setProperty to set the global scene property to the inputed value
			\param		key			<str> || <QString>
			\param		value		<variant>
			\return		<bool>
		"""
		return setattr( mxs, str(key), self._toNativeValue( value ) )
	
	def softwareId( self ):
		"""
			\remarks	implements AbstractScene.softwareId to return a unique version/bits string information that will represent the exact
									version of the software being run.
			\return		<str>
		"""
		# show the bit amount
		output = '%s_x32'
		if ( mxs.is64bitApplication() ):
			output = '%s_x64'
			
		return output % str( mxs.maxversion()[0] )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'Scene', StudiomaxScene )