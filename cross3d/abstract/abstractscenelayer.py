##
#	\namespace	blur3d.api.abstract.abstractscenelayer
#
#	\remarks	The AbstractSceneLayer provides a cross-application interface to 3d scene layer's and their interaction
#				This class will provide the base implementation and definition of methods that will need to be re-implemented
#				to hanel per-application usage
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from abstractsceneobjectgroup import AbstractSceneObjectGroup

class AbstractSceneLayer( AbstractSceneObjectGroup ):
	def __init__( self, scene, nativeLayer ):
		AbstractSceneObjectGroup.__init__( self, scene, nativeLayer )
		
		# define custom properties
		self._altMtlIndex		= -1
		self._altPropIndex		= -1
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeAltMaterials( self ):
		"""
			\remarks	[abstract] return a list of the alternate materials associated with this layer
			\sa			altMaterialCount, altMaterialAt, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterials
						setCurrentAltMaterialIndex, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeLayerGroup( self ):
		"""
			\remarks	[abstract] return the layer group that this layer belongs to
			\sa			layerGroup, setLayerGroup, _setNativeLayerGroup
			\return		<variant> nativeLayerGroup || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	[abstract] return the native value for this layer's property defined by the key
			\param		key			<str>
			\param		default		<variant>	value to return if not found
			\return		<variant> nativeValue
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return default
	
	def _setNativeAltMaterialAt( self, index, nativeMaterial ):
		"""
			\remarks	[abstract] set the material in the alternate materials list at the inputed index to the given material
			\param		index			<index>
			\param		nativeMaterial	<variant> || None
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeAltMaterials( self, nativeMaterials ):
		"""
			\remarks	[abstract] set the alternate material list for this layer
			\param		nativeMaterials	<list> [ <variant> nativeMaterial, .. ]
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeLayerGroup( self, nativeLayerGroup ):
		"""
			\remarks	[abstract] set the layer group that this layer belongs to
			\sa			layerGroup, setLayerGroup, _nativeLayerGroup
			\param		<variant> nativeLayerGroup || None
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	[abstract] return the native value for this layer's property defined by the key
			\param		key				<str>
			\param		nativeValue		<variant>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeWireColor( self, nativeColor ):
		"""
			\remarks	[abstract] set the wirecolor for this layer instance
			\sa			setWireColor
			\param		nativeColor		<variant>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _nativeWireColor( self ):
		"""
			\remarks	[abstract] return the wirecolor for this layer instance
			\sa			nativeColor
			\return		<variant> nativeColor || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def addAltMaterial( self, material ):
		"""
			\remarks	add the inputed material to the list of possible alternate materials for this layer
			\sa			altMaterials, setAltMaterials
			\param		material	<blur3d.api.SceneMaterial>
			\return		<bool> success
		"""
		altMtls = self.altMaterials()
		altMtls.append( material )
		return self.setAltMaterials( altMtls )
	
	def addAltPropSet( self, propSet ):
		"""
			\remarks	add the property set to the list of possible alternate property sets for this layer
			\sa			altPropSets, setAltPropSets
			\param		propSet		<blur3d.api.ScenePropSet>
			\return		<bool> success
		"""
		propSets = self.altPropSets()
		propSets.append( propSet )
		return self.setAltPropSets( propSets )
		
	def altMaterialAt( self, index ):
		"""
			\remarks	retrieve the alternate material at the inputed index
			\sa			altMaterialCount, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterials, 
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\param		index	<int>
			\return		<blur3d.api.SceneMaterial> || None
		"""
		mtls = self._nativeAltMaterials()
		if ( 0 <= index and index < len(mtls) ):
			mtl = mtls[index]
			if ( mtl ):
				from blur3d.api import SceneMaterial
				return SceneMaterial( self._scene, mtl )
			else:
				return None
		return None
	
	def altMaterialCount( self ):
		"""
			\remarks	return the number of alternate materials that this layer is associated with
			\sa			altMaterialAt, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterials, 
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<int> count
		"""
		return len( self._nativeAltMaterials() )
	
	def altMaterials( self ):
		"""
			\remarks	return a list of the alternate materials held by this layer
			\sa			altMaterialAt, altMaterialCount, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterials, 
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<list> [ <blur3d.api.SceneMaterial>, .. ]
		"""
		from blur3d.api import SceneMaterial
		output = []
		for mtl in self._nativeAltMaterials():
			if ( mtl ):
				output.append( SceneMaterial( self._scene, mtl ) )
			else:
				output.append( None )
		return output
	
	def altMaterialFlags( self ):
		"""
			\remarks	[abstract] return a list of material duplication flags for this layer
			\return		<list> [ <blur3d.constants.MaterialDuplicateOptions>, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def altMaterialFlagsAt( self, index ):
		"""
			\remarks	return the material flags at the inputed index
			\param		index	<int>
			\return		<blur3d.constants.MaterialDuplicateOptions>
		"""
		flags = self.altMaterialFlags()
		if ( 0 <= index and index < len(flags) ):
			return flags[index]
		return 0
	
	def altPropSetAt( self, index ):
		"""
			\remarks	retrive the alternate SceneObjectPropSet at the inputed index
			\sa			altPropSetCount, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<blur3d.api.SceneObjectPropSet> || None
		"""
		propsets = self.altPropSets()
		if ( 0 <= index and index < len(propsets) ):
			return propsets[index]
		return None
	
	def altPropSetCount( self ):
		"""
			\remarks	retrive the number of alternate SceneObjectPropSet's for this layer
			\sa			altPropSetAt, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<int> count
		"""
		return len( self.altPropSets() )
	
	def altPropSets( self ):
		"""
			\remarks	[abstract]	retrive the alternate SceneObjectPropSet's for this layer
			\sa			altPropSetCount, altPropAt, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<list> [ <blur3d.api.SceneObjectPropSet>, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def currentAltMaterialIndex( self ):
		"""
			\remarks	retrive the index of the currently applied alternate material for this layer
			\sa			altMaterialAt, altMaterialCount, altMaterials, currentAltMaterial, setAltMaterialAt, setAltMaterials, 
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<int> index
		"""
		return self._altMtlIndex
	
	def currentAltMaterial( self ):
		"""
			\remarks	retrive the index of the currently applied alternate material for this layer
			\sa			altMaterialAt, altMaterialCount, altMaterials, currentAltMaterialIndex, setAltMaterialAt, setAltMaterials, 
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<int> index
		"""
		return self.altMaterialAt( self._altMtlIndex )
	
	def currentAltPropSetIndex( self ):
		"""
			\remarks	retrive the alternate object property set at the inputed index
			\sa			altPropSetCount, altPropSetAt, altPropSets, currentAltPropSet, setAltPropSetAt, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<int> index
		"""
		return self._altPropIndex
		
	def currentAltPropSet( self ):
		"""
			\remarks	retrive the alternate object property set at the inputed index
			\sa			altPropSetCount, altPropSetAt, altPropSets, currentAltPropSetIndex, setAltPropSetAt, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<int> index
		"""
		return self.altPropSetAt( self._altPropIndex )
	
	def hasAltMaterialFlagAt( self, index, flag ):
		"""
			\remarks	return whether or not a given material duplication flag is set for the inputed alt material index
			\param		index	<int>
			\param		flag	<blur3d.constants.MaterialDuplicateOptions>
			\return		<bool> found
		"""
		flags = self.altMaterialFlags()
		if ( 0 <= index and index < len( flags ) ):
			return (flags[index] & flag) != 0
		return False
	
	def hasProperty( self, key ):
		"""
			\remarks	[abstract] return whether or not a given property exists for this layer
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def indexOfAltMaterial( self, material ):
		"""
			\remarks	return the index of the inputed material for the current layer
			\param		material	<blur3d.api.SceneMaterial>
			\return		<int> index (-1 if not found)
		"""
		mtls = self.altMaterials()
		try:
			return mtls.index(material)
		except:
			return -1
	
	def indexOfAltPropSet( self, propSet ):
		"""
			\remarks	return the index of the inputed property set for the current layer
			\param		propSet		<blur3d.api.ScenePropSet>
			\return		<int> index (-1 if not found)
		"""
		propSets = self.altPropSets()
		try:
			return propSets.index(propSet)
		except:
			return -1
	
	def isActive( self ):
		"""
			\remarks	[abstract] return whether or not this layer is currently active in the scene
			\sa			setActive
			\return		<bool> active
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def isWorldLayer( self ):
		"""
			\remarks	[abstract] return whether or not this layer is the root world layer of the scene
			\return		<bool> is world
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def isolate( self ):
		"""
			\remarks	reimplements the AbstractSceneObjectGroup.isolate method to isolate just this layer (hide all other layers)
			\return		<bool> success
		"""
		scene = self._scene
		
		for layer in scene.layers():
			if ( not layer == self ):
				layer.hide()
			else:
				layer.unhide()
				
		scene.emitLayerStateChanged()
		return True
	
	def groupName( self ):
		"""
			\remarks	implements the AbstractSceneObjectGroup.groupName method to retrieve the group name for this object group instance
			\return		<str> name
		"""
		layerGroup = self.layerGroup()
		if ( layerGroup ):
			return layerGroup.groupName()
		return ''
	
	def layerGroup( self ):
		"""
			\remarks	return the layer group that this layer belongs to
			\sa			_nativeLayerGroup
			\return		<blur3d.api.SceneLayerGroup> || None
		"""
		nativeGroup = self._nativeLayerGroup()
		if ( nativeGroup ):
			from blur3d.api import SceneLayerGroup
			return SceneLayerGroup( self._scene, nativeGroup )
		return None
	
	def layerGroupOrder( self ):
		"""
			\remarks	[abstract] return the sort order for this layer within its layer group
			\sa			setLayerGroupOrder
			\return		<int> index
		"""
		from blurdev import debug
		
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return -1
	
	def layerName( self ):
		"""
			\remarks	[abstract] retrieve the layer name for this layer
			\sa			groupName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return ''
		
	def layerId( self ):
		"""
			\remarks	[abstract] retrieve the unique layer id for this layer instance
			\sa			setLayerId
			\return		<int> id
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0
		
	def property( self, key, default = None ):
		"""
			\remarks	return the given property from this layer
			\sa			hasProperty, setProperty, _nativeProperty, _setNativeProperty
			\param		key			<str>
			\param		default		<variant>	default return value for a non-found property
			\return		<variant> value
		"""
		nativeValue = self._nativeProperty( key )
		if ( nativeValue != None ):
			return self._scene._fromNativeValue( nativeValue )
		return default
	
	def recordXml( self, xml ):
		"""
			\remarks	define a way to record this layer to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', 	self.layerName() )
		xml.setAttribute( 'id', 	self.layerId() )
		return True
	
	def recordLayerState( self, xml ):
		"""
			\remarks	records the layer's current state to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		# don't bother recording hidden layers
		if ( not self.isVisible() ):
			return False
		
		# record the layer state
		node = xml.addNode( 'layer' )
		node.setAttribute( 'name', 		self.layerName() )
		node.setAttribute( 'id', 		self.layerId() )
		
		# record the propSetOverride
		propSet = self.propSetOverride()
		if ( propSet ):
			propSet.recordXml( node.addNode( 'propSetOverride' ) )
		
		# record the material override
		material = self.materialOverride()
		if ( material ):
			material.recordXml( node.addNode( 'materialOverride' ) )
		
		# record the environment override for the world layer
		if ( self.isWorldLayer() ):
			override = self._scene.environmentMapOverride()
			if ( override ):
				override.recordXml( node.addNode( 'environmentMapOverride' ) )
		
		return True
	
	def restoreLayerState( self, xml ):
		"""
			\remarks	restore the layer's state from the inputed xml
			\param		xml		<blurdev.XML.XMLDocument>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		# set visible
		self.setVisible(True)
		
		# determine the alterante state for this layer
		scene = self._scene
		from blur3d.api import SceneMaterial, SceneMap, SceneObjectPropSet
		self.setPropSetOverride( 	SceneObjectPropSet.fromXml( scene, xml.findChild( 'propSetOverride' ) ) )
		self.setMaterialOverride( 	SceneMaterial.fromXml( 		scene, xml.findChild( 'materialOverride' ) ) )
		
		# restore environment override
		if ( self.isWorldLayer() ):
			scene.setEnvironmentMapOverride( SceneMap.fromXml( scene, xml.findChild( 'environmentMapOverride' ) ) )
	
	def removeAltMaterialAt( self, index ):
		"""
			\remarks	remove the material at the inputed index from the material list
			\param		index	<int>
			\return		<bool> success
		"""
		altMtls = self.altMaterials()
		if ( 0 <= index and index < len(altMtls) ):
			return self.setAltMaterials( altMtls[:index] + altMtls[index+1:] )
		return False
	
	def removeAltPropSetAt( self, index ):
		"""
			\remarks	remove the propset at the inputed index from this layer's list of alternate property sets
			\param		index	<int>
			\return		<bool> success
		"""
		altPropSets = self.altPropSets()
		if ( 0 <= index and index < len(altPropSets) ):
			return self.setAltPropSets( altPropSets[:index] + altPropSets[index+1:] )
		return False
	
	def setActive( self, state ):
		"""
			\remarks	[abstract] mark this layer as the active scene layer
			\sa			isActive
			\param		state	<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setAltMaterialAt( self, index, material ):
		"""
			\remarks	sets the alternate material at the inputed index to the given material instance
			\sa			altMaterialCount, altMaterialAt, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterials
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<bool> success
		"""
		nativePointer = None
		if ( material ):
			nativePointer = material.nativePointer()
			
		return self._setNativeAltMaterialAt( index, nativePointer )
	
	def setAltMaterials( self, materials ):
		"""
			\remarks	sets the alternate material list for this layer
			\sa			altMaterialCount, altMaterialAt, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterialAt
						setCurrentAltMaterialIndex, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<bool> success

		"""
		mtls = []
		for mtl in materials:
			if ( mtl ):
				mtls.append( mtl.nativePointer() )
			else:
				mtls.append( None )
				
		return self._setNativeAltMaterials( mtls )
	
	def setAltMaterialFlagAt( self, index, flag, state = True ):
		"""
			\remarks	set whether or not a given material duplication flag is on for the inputed alt material index
			\param		index	<int>
			\param		flag	<blur3d.constants.MaterialDuplicateOptions>
			\param		state	<bool> on
			\return		<bool> success
		"""
		flags = self.altMaterialFlags()
		if ( 0 <= index and index < len( flags ) ):
			if ( state ):
				flags[index] |= flag
			else:
				flags[index] ^= flag
				
			return self.setAltMaterialFlags( flags )
		return False
	
	def setAltMaterialFlagsAt( self, index, flags ):
		"""
			\remarks	set the alternate material flags at the inputed index for this instance
			\param		index	<int>
			\param		flags	<blur3d.constants.MaterialDuplicateOptions>
			\return		<bool> success
		"""
		mflags = self.altMaterialFlags()
		if ( 0 <= index and index < len( mflags ) ):
			mflags[index] = flags
			return self.setAltMaterialFlags( mflags )
		return False
				
	def setAltMaterialFlags( self, flags ):
		"""
			\remarks	[abstract] set the alternate material flags for this instance
			\param		flags	<list> [ <blur3d.constants.MaterialDuplicateOptions>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setAltPropSetAt( self, index, propSet ):
		"""
			\remarks	[abstract] set the alternate object property set at the inputed index
			\sa			altPropSetCount, altPropSetAt, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setAltPropSets( self, propSets ):
		"""
			\remarks	[abstract] set the alternate object property set list for this layer
			\sa			altPropSetCount, altPropSetAt, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt, 
						setCurrentAltPropSetIndex
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setCurrentAltMaterialIndex( self, index ):
		"""
			\remarks	set the current index for the alternate material, applying the alternate material when necessary
			\sa			setMaterialOverride, altMaterialCount, altMaterialAt, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterialAt
						setAltMaterials, _nativeAltMaterials, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<bool> changed
		"""
		# do not need to reprocess
		if ( index == self._altMtlIndex ):
			return False
		
		mtls = self.altMaterials()
		
		# apply an override state
		if ( 0 <= index and index < len(mtls) ):
			self._altMtlIndex = index
			return self.setMaterialOverride( mtls[index], options = self.altMaterialFlagsAt(index) )
			
		# clear an override state
		elif ( index == -1 ):
			self._altMtlIndex = index
			return self.clearMaterialOverride()
			
		return False
	
	def setCurrentAltPropSetIndex( self, index ):
		"""
			\remarks	set the current index for the alternate object property set, applyting the set to the objects on this layer when necessary
			\sa			setPropSetOverride, altPropSetCount, altPropSetAt, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt, 
						setAltPropSets
			\return		<bool> changed
		"""
		# do not need to reprocess
		if ( index == self._altPropIndex ):
			return False
		
		propsets = self.altPropSets()
		
		# apply an override state
		if ( 0 <= index and index < len(propsets) ):
			if ( self.setPropSetOverride( propsets[index] ) ):
				self._altPropIndex = index
				return True
			return False
		
		# clear the override state
		elif ( index == -1 ):
			if ( self.clearPropSetOverride() ):
				self._altPropIndex = index
				return True
			return False
			
		else:
			return False
	
	def setGroupName( self, name ):
		"""
			\remarks	implements the AbstractSceneObjectGroup.groupName method to set the group name for this object group instance
			\sa			setLayerName
			\param		name	<str>
			\return		<bool> success
		"""
		layerGroup = self._scene.findLayerGroup( name)
		if ( layerGroup ):
			return self.setLayerGroup( layerGroup )
		return False
	
	def setLayerName( self, name ):
		"""
			\remarks	[abstract] set the layer name for this layer
			\sa			setGroupName
			\param		name	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setLayerGroup( self, layerGroup ):
		"""
			\remarks	set the layer group that this layer is associated with
			\sa			layerGroup, _setNativeLayerGroup
			\param		layerGroup	<blur3d.api.SceneLayerGroup> || None
			\return		<bool> success
		"""
		nativeGroup = None
		if ( layerGroup ):
			nativeGroup = layerGroup.nativePointer()
		
		return self._setNativeLayerGroup( nativeGroup )
	
	def setLayerGroupOrder( self, groupOrder ):
		"""
			\remarks	set the layer group sort order for this layer within its layer group
			\sa			layerGroupOrder
			\param		groupOrder		<int>
			\return		<bool> changed
		"""
		from blurdev import debug
		
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	def setLayerId( self, layerId ):
		"""
			\remarks	[abstract] set the unique layer id for this layer instance
			\sa			layerId
			\param		layerId		<int>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setProperty( self, key, value ):
		"""
			\remarks	set the property for this layer defined by the inputed key to the inputed value
			\sa			hasProperty, property, _nativeProperty, _setNativeProperty
			\param		key			<str>
			\param		value		<variant>
			\return		<bool> success
		"""
		return self._setNativeProperty( str(key), self._scene._toNativeValue( value ) )
	
	def setWireColor( self, color ):
		"""
			\remarks	set the wire color for this layer
			\sa			wireColor, _setNativeWireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		return self._setNativeWireColor( self._scene._toNativeValue( color ) )
	
	def wireColor( self ):
		"""
			\remarks	return the wire color for this layer
			\sa			setWireColor, _nativeWireColor
			\return		<QColor>
		"""
		clr = self._nativeWireColor()
		if ( clr ):
			return self._scene._fromNativeValue( clr )
			
		from PyQt4.QtGui import QColor
		return QColor()
	
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	create a new layer from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		if ( xml ):
			return scene.findLayer( layerName = xml.attribute( 'name' ), layerId = int(xml.attribute( 'id',0 )) )
		return None
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneLayer', AbstractSceneLayer, ifNotFound = True )