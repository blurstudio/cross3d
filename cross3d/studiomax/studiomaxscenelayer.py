##
#	\namespace	cross3d.studiomax.studiomaxscenelayer
#
#	\remarks	The StudiomaxSceneLayer class provides implementation of the AbstractSceneLayer class as it applys to 3d Studio Max scenes
#
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax import mxs
import cross3d
from cross3d.abstract.abstractscenelayer import AbstractSceneLayer
from cross3d import SceneObject

#-----------------------------------------------------------------------------

from mxscustattribdef import MXSCustAttribDef

class LayerMetaData( MXSCustAttribDef ):
	version 	= 1.63

	def addAltMtlSlot( self ):
		altMtls = list( self.value( 'altMtls', [] ) )
		displ	= list( self.value( 'keepDisplacement', [] ) )
		opac	= list( self.value( 'keepOpacity', [] ) )

		altMtls.append( None )
		displ.append( False )
		opac.append( False )

		self.setValue( 'altMtls', altMtls )
		self.setValue( 'keepDisplacement', displ )
		self.setValue( 'keepOpacity', opac )

		return True

	def addAltPropSlot( self ):
		values 		= list( self.value( 'altPropValues', [] ) )
		usages 		= list( self.value( 'altPropUsages', [] ) )
		ids 		= list( self.value( 'altPropIds', [] ) )

		from cross3d import SceneObjectPropSet
		baseProp = SceneObjectPropSet( None, None )

		values.append( baseProp._valueString() )
		usages.append( baseProp._activeString() )
		ids.append( mxs.blurUtil.genUniqueId() )

		self.setValue( 'altPropValues', values )
		self.setValue( 'altPropUsages', usages )
		self.setValue( 'altPropIds', ids )

		return True

	def init( self ):
		MXSCustAttribDef.init( self )

		self.setValue( 'version', LayerMetaData.version )

		# set the default first alt material
		self.addAltMtlSlot()

		# set the default first alt property
		self.addAltPropSlot()

	def removeAltMtlSlot( self, index ):
		altMtls 		= list( self.value( 'altMtls' ) )
		displacements 	= list( self.value( 'keepDisplacement' ) )
		opacities		= list( self.value( 'keepOpacity' ) )

		# remove the alternate materials
		if ( 0 <= index and index < len( altMtls ) ):
			# update the current index to reflect the changes
			cindex = self.value( 'currentAltMtlIndex' )
			if ( index < cindex ):
				self.setValue( 'currentAltMtlIndex', cindex - 1 )

			altMtls 		= altMtls[:index] + altMtls[index+1:]
			displacements 	= displacements[:index] + displacements[index+1:]
			opacities		= opacities[:index] + opacities[index+1:]

			self.setValue( 'altMtls', altMtls )
			self.setValue( 'keepDisplacement', displacements )
			self.setValue( 'keepOpacity', opacities )

			return True
		return False

	def removeAltPropSlot( self, index ):
		altPropValues 	= list( self.value( 'altPropValues' ) )
		altPropUsages 	= list( self.value( 'altPropUsages' ) )
		altPropIds		= list( self.value( 'altPropIds' ) )

		# remove the alternate properties
		if ( 0 <= index and index < len( altPropValues ) ):
			# update the current index to reflect the changes
			cindex = self.value( 'currentAltPropIndex' )
			if ( index < cindex ):
				self.setValue( 'currentAltPropIndex', cindex - 1 )

			altPropValues 	= altPropValues[:index] + altPropValues[index+1:]
			altPropUsages 	= altPropUsages[:index] + altPropUsages[index+1:]
			altPropIds 		= altPropIds[:index] + altPropIds[index+1:]

			self.setValue( 'altPropValues', altPropValues )
			self.setValue( 'altPropUsages', altPropUsages )
			self.setValue( 'altPropIds', altPropIds )

			return True
		return False

	@classmethod
	def define( cls ):
		cls.setAttrName( 'OnionData' )

		# define overall parameters
		cls.defineParam( 'version', 		'float',			paramId = 'v' )
		cls.defineParam( 'layerName', 		'string', 			paramId = 'lnm' )
		cls.defineParam( 'layerId', 		'integer', 			paramId = 'lid' )

		# define grouping parameters
		cls.defineParam( 'groupIndex',		'integer',			paramId = 'gi' )
		cls.defineParam( 'groupOrder',		'integer',			paramId = 'go' )

		# define alternate material parameters per layer
		cls.defineParam( 'currentAltMtlIndex',	'integer',			paramId = 'mi' )
		cls.defineParam( 'altMtls',				'materialTab',		paramId = 'am' )
		cls.defineParam( 'keepDisplacement',	'boolTab',			paramId = 'kd' )
		cls.defineParam( 'keepOpacity',			'boolTab',			paramId = 'ko' )

		# define alternate material overrides per base material
		cls.defineParam( 'baseMtlIds',		'intTab',			paramId = 'oi' )
		cls.defineParam( 'baseMtlNames',	'stringTab',		paramId = 'ns' )
		cls.defineParam( 'altMtlIndexes',	'intTab',			paramId = 'omi' )
		cls.defineParam( 'overrideMtls',	'materialTab',		paramId = 'om' )

		# define alternate properties per layer
		cls.defineParam( 'currentAltPropIndex',	'integer',			paramId = 'pi' )
		cls.defineParam( 'altPropValues',		'stringTab',		paramId = 'ap' )
		cls.defineParam( 'altPropUsages',		'stringTab',		paramId = 'up' )
		cls.defineParam( 'altPropIds',			'intTab',			paramId = 'id' )

		# define mental ray properties
		cls.defineParam( 'mrShaderIndex',	'integer',			paramId = 'si' )
		cls.defineParam( 'mrShaderMap',		'textureMap',		paramId = 'sl' )

		# define material library index
		cls.defineParam( 'mtlLibindex',		'integer',			paramId = 'li' )

		# define fx linkage
		cls.defineParam( 'linkedFx',		'intTab',			paramId = 'fx' )

		# define atmospheric linkage
		cls.defineParam( 'linkedAtmos',		'intTab',			paramId = 'atm' )

# register the definition to 3dsmax
LayerMetaData.register()

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneLayer( AbstractSceneLayer ):
	def __init__( self, scene, nativeLayer ):
		AbstractSceneLayer.__init__( self, scene, nativeLayer )

		# create custom properties
		self._metaData 			= None
		self._altPropCache		= None
		self._altMtlCache		= None
		self._altMtlFlagsCache	= None

		# initialize the data properly
		self._altMtlIndex		= self.metaData().value( 'currentAltMtlIndex', 0 ) - 1
		self._altPropIndex		= self.metaData().value( 'currentAltPropIndex', 0 ) - 1

	def __syncNativeObjects( self, nativeObjects ):
		# match the layer's override state to the objects
		mtl = self._nativeMaterialOverride()
		if ( mtl ):
			self._scene._setNativeMaterialOverride( nativeObjects, mtl, options = self.materialOverrideFlags(), advancedState = self.materialOverrideAdvancedState() )
		else:
			self._scene._clearNativeMaterialOverride( nativeObjects )

		propSet = self._nativePropSetOverride()
		if ( propSet ):
			self._scene._setNativePropSetOverride( nativeObjects, propSet )
		else:
			self._scene._clearNativePropSetOverride( nativeObjects )

		return True

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _addNativeAtmospherics( self, nativeAtmos ):
		"""
			\remarks	implements the AbstractSceneObjectGroup._addNativeAtmospherics method to add a list of atmospherics to this layer
			\param		nativeAtmos		<list> [ <Py3dsMax.mxs.Atmospheric> || <Py3dsMax.mxs.Effect> nativeAtmos ]
			\return		<bool> success
		"""
		data 		= self.metaData()
		atm 		= list(data.value('linkedAtmos'))
		unique_id	= mxs.blurUtil.uniqueId

		for atmos in nativeAtmos:
			uid = unique_id( atmos )
			if ( not uid in atm ):
				atm.append( uid )

		data.setValue( 'linkedAtmos', atm )

		# reset the id's on other layers
		for layer in self._scene.layers():
			if ( layer == self ):
				continue

			latm = list(layer.metaData().value( 'linkedAtmos' ))
			latm = [ i for i in latm if not i in atm ]
			layer.metaData().setValue( 'linkedAtmos', latm )

		return True

	def _addNativeFx(self, nativeFx):
		"""
			\remarks	implements the AbstractSceneObjectGroup._addNativeFx method to add a list of Fx to this layer
			\param		nativeFx	<list>
			\return		<bool> success
		"""
		data = self.metaData()
		fxIds = list(data.value('linkedFx'))
		unique_id = mxs.blurUtil.uniqueId

		for fx in nativeFx:
			uid = unique_id(fx)
			if not uid in fxIds:
				fxIds.append(uid)

		data.setValue('linkedFx', fxIds)
		return True

	def _addNativeObjects( self, nativeObjects ):
		"""
			\remarks	implements the AbstractSceneObjectGroup._addNativeObjects method to add the native objects to the layer
			\sa			addObjects, addSelection
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		# add the nodes to this layer
		addnode = self._nativePointer.addNode
		hidden = self._nativePointer.isHidden
		frozen = self._nativePointer.isfrozen

		for obj in nativeObjects:
			addnode(obj)
			obj.ishidden = hidden
			obj.isfrozen = frozen

		self.__syncNativeObjects(nativeObjects)
		return True

	def _clearNativeObjects( self ):
		"""
			\remarks	implements the AbstractSceneObjectGroup._clearNativeObjects method to clear the native objects from this layer
			\sa			clearObjects
			\return		<bool> success
		"""
		worldlayer = mxs.layerManager.getLayer(0)

		# cannot clear objects off the world layer - we have no where to move them
		if ( worldlayer == self._nativePointer ):
			return False

		nativeObjects = mxs.pyhelper.getLayerNodes( self._nativePointer )

		addnode = worldlayer.addNode
		for obj in nativeObjects:
			addnode(obj)

		return True

	def _clearNativeMaterialOverride( self ):
		"""
			\remarks	reimplements the AbstractSceneObjectGroup._clearNativeMaterialOverride method to clear
			\return		<bool> success
		"""
		# check to see if we are setting this to one of our cached native material indexes
		data = self.metaData()
		data.setValue( 'mtlLibindex', 			0 )
		data.setValue( 'currentAltMtlIndex', 	0 )
		data.setValue( 'mrShaderIndex', 		0 )

		self._altMtlIndex = -1

		return AbstractSceneLayer._clearNativeMaterialOverride( self )

	def _nativeAltMaterials( self ):
		"""
			\remarks	implements the AbstractSceneLayer._nativeAltMaterials method to return a list of the alternate materials associated with this layer
			\sa			altMaterialCount, altMaterialAt, altMaterials, currentAltMaterial, currentAtlMaterialIndex, setAltMaterialAt, setAltMaterials
						setCurrentAltMaterialIndex, _setNativeAltMaterials, _setNativeAltMaterialAt
			\return		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
		"""
		if ( self._altMtlCache == None ):
			self._altMtlCache = list(self.metaData().value( 'altMtls' ))

		return self._altMtlCache

	def _nativeAtmospherics( self ):
		"""
			\remarks	implements the AbstractObjectGroup._nativeAtmospherics method to return a list of the atmospheric instances linked to this layer
			\return		<list> [ <Py3dsMax.mxs.Atmospheric> || <Py3dsMax.mxs.Effect> nativeAtmospheric, .. ]
		"""
		unique_id 	= mxs.blurUtil.uniqueId
		atm			= list(self.metaData().value('linkedAtmos'))
		get_atmos	= mxs.getAtmospheric
		get_effect	= mxs.getEffect
		output		= []

		# collect the atmospherics
		for i in range( mxs.numAtmospherics ):
			atmos 	= get_atmos(i+1)
			uid		= unique_id(atmos)
			if ( uid in atm ):
				output.append(atmos)

		# collect the effects
		for i in range( mxs.numEffects ):
			effect	= get_effect(i+1)
			uid		= unique_id(effect)
			if ( uid in atm ):
				output.append(effect)

		return output

	def _nativeFxs(self):
		"""
			\remarks	implements the AbstractObjectGroup._nativeFxs method to return a list of the fx instances linked to this layer
			\return		<list> [ nativeAtmospheric, .. ]
		"""
		layerFxIds = list(self.metaData().value('linkedFx'))
		fxInstances = [f.nativePointer() for f in self.scene().fxs() if mxs.blurUtil.uniqueId(f.nativePointer()) in layerFxIds]
		return fxInstances

	def _nativeLayerGroup( self ):
		"""
			\remarks	implements the AbstractSceneLayer._nativeLayerGroup method to retrieve the SceneLayerGroup that this layer belongs to
			\return		<cross3d.SceneLayerGroup>
		"""
		index	= self.metaData().value( 'groupIndex' ) - 1
		names 	= list(self._scene.metaData().value('layerGroupNames'))
		if ( 0 <= index and index < len( names ) ):
			return names[index]
		return ''

	def _nativeObjects( self ):
		"""
			\remarks	implements the AbstractSceneObjectGroup._nativeObjects method to return a list of the native objects that are currently on this layer
			\sa			objects
			\return		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
		"""
		layerNodes = mxs.pyhelper.getLayerNodes(self._nativePointer)
		layerNodes.reverse()
		return layerNodes

	def _nativeMaterials(self, baseMaterials=False):
		"""
			\remarks	implements the AbstractSceneObjectGroup._nativeMaterials method to return a list of the native materials that are currently on this layer
			\sa			materials
			\return		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
		"""
		mtls = []
		for obj in self._nativeObjects():
			if baseMaterials and self.materialOverride():
				from cross3d.constants import MaterialCacheType
				from cross3d.studiomax import StudiomaxAppData
				get_userprop = mxs.getUserProp
				get_appdata	= mxs.getAppData
				mid = get_appdata(obj, int(StudiomaxAppData.AltMtlIndex))
				if mid == None:
					mid = get_userprop(obj, 'basematerial')
				omtl = self.scene()._cachedNativeMaterial(MaterialCacheType.BaseMaterial, mid)
			else:
				omtl = obj.material
			if omtl and not omtl in mtls:
				mtls.append(omtl)
		return mtls

	def _nativeMaterialOverride( self ):
		data = self.metaData()

		# load the material from the alternate materials
		index = data.value( 'currentAltMtlIndex' )
		if ( index ):
			mtls = list(data.value( 'altMtls' ))
			index -= 1
			if ( 0 <= index and index < len(mtls) ):
				return mtls[index]
			else:
				cross3d.logger.debug('%i index is out of range of %i alt materials for %s layer.' % (index,len(mtls),self.name()))
				return None

		# load the material from the material library
		index = data.value( 'mtlLibindex' )
		if ( index ):
			from cross3d.constants import MaterialCacheType
			mtls = self._scene._cachedNativeMaterials( MaterialCacheType.MaterialOverrideList )
			index -= 1
			if ( 0 <= index and index < len(mtls) ):
				return mtls[index]

		return None

	def _nativePropSetOverride( self ):
		data = self.metaData()

		# load the propset
		index = data.value( 'currentAltPropIndex' )
		if ( index ):
			propSets = self.altPropSets()
			index 	-= 1

			if ( 0 <= index and index < len(propSets) ):
				return propSets[index]
			else:
				cross3d.logger.debug('%i index is out of range of %i alt propsets for %s layer.' % (index,len(propSets),self.name()))
				return None

		return None

	def _setNativeAltMaterialAt( self, index, nativeMaterial ):
		"""
			\remarks	implements the AbstractSceneLayer._setNativeAltMaterialAt method to set the material in the alternate materials list at the inputed index to the given material
			\param		index			<index>
			\param		nativeMaterial	<Py3dsMax.mxs.Material> || None
			\return		<bool> success
		"""
		altMaterials = self._nativeAltMaterials()
		if ( 0 <= index and index < len( altMaterials ) ):
			altMaterials[index] = nativeMaterial
			return self._setNativeAltMaterials( altMaterials )
		return False

	def _setNativeAltMaterials( self, nativeMaterials ):
		"""
			\remarks	implements the AbstractSceneLayer._setNativeAltMaterials method to set the alternate material list for this layer
			\param		nativeMaterials	<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
			\return		<bool> success
		"""
		mtls = list( nativeMaterials )
		data = self.metaData()

		# make sure we have the proper amount of displacements/opacities
		opac 	= list(data.value( 'keepOpacity' ))
		displ 	= list(data.value( 'keepDisplacement' ))

		mtlcount = len(mtls)
		while ( len(opac) < mtlcount ):
			opac.append(False)

		while ( len(displ) < mtlcount ):
			displ.append(False)

		# set the data
		data.setValue( 'altMtls', mtls )
		data.setValue( 'keepOpacity', opac )
		data.setValue( 'keepDisplacement', displ )

		self._altMtlCache = mtls
		self._altMtlFlagsCache = None
		return True

	def _setNativeMaterialOverride( self, nativeMaterial, options = -1, advancedState = None ):
		"""
			\remarks	reimplements the AbstractSceneObjectGroup._setNativeMaterialOverride method to set the overriden material for this layer instance,
						marking that it is using a material from the global material cache if necessary
			\param		nativeMaterial	<Py3dsMax.mxs.Material>
			\return		<bool> success
		"""
		# check to see if we are setting this to one of our cached native material indexes
		data = self.metaData()
		if ( nativeMaterial ):
			from cross3d.constants import MaterialCacheType

			# set the native alternatematerial
			altmtls = self._nativeAltMaterials()
			if ( nativeMaterial in altmtls ):
				index = altmtls.index(nativeMaterial)
				self._altMtlIndex = index
				data.setValue( 'mtlLibindex', 			0 )
				data.setValue( 'currentAltMtlIndex', 	index + 1 )
				data.setValue( 'mrShaderIndex', 		0 )

			else:
				# see if the material is in the material library
				nativeMaterials = list(self._scene._cachedNativeMaterials( MaterialCacheType.MaterialOverrideList ))
				if ( nativeMaterial in nativeMaterials ):
					self._altMtlIndex = -1
					data.setValue( 'mtlLibindex', 			nativeMaterials.index(nativeMaterial) + 1 )
					data.setValue( 'currentAltMtlIndex', 	0 )
					data.setValue( 'mrShaderIndex', 		0 )

		# clear the alternate material state
		else:
			self._altMtlIndex = -1
			data.setValue( 'mtlLibindex', 			0 )
			data.setValue( 'currentAltMtlIndex', 	0 )
			data.setValue( 'mrShaderIndex', 		0 )


		return AbstractSceneLayer._setNativeMaterialOverride( self, nativeMaterial, options = options, advancedState = advancedState )

	def _setNativePropSetOverride( self, nativePropSet ):
		"""
			\remarks	reimplements the AbstractSceneObjectGroup._setNativePropSetOverride method to set the overriden propset for this layer instance,
						marking that it is using a propset from the global propset cache if necessary
			\param		nativePropSet	<cross3d.ScenePropSet>
			\return		<bool> success
		"""
		# check to see if we are setting this to one of our cached native propset indexes
		data = self.metaData()
		if ( nativePropSet ):
			mpropset = self.altPropSets()
			if ( nativePropSet in mpropset ):
				index	= mpropset.index(nativePropSet)
				nativePropSet = mpropset[index]
				data.setValue( 'currentAltPropIndex', index + 1 )
			else:
				data.setValue( 'currentAltPropIndex', 0 )
				nativePropSet = None
		else:
			data.setValue( 'currentAltPropIndex', 0 )
			nativePropSet = None

		return AbstractSceneLayer._setNativePropSetOverride( self, nativePropSet )

	def _setNativeLayerGroup( self, nativeLayerGroup ):
		"""
			\remarks	implements the AbstractSceneLayer._setNativeLayerGroup method to set the layer group that this layer belongs to
			\sa			layerGroup, setLayerGroup, _nativeLayerGroup
			\param		<str> nativeLayerGroup || None
			\return		<bool> success
		"""
		names	= list(self._scene.metaData().value('layerGroupNames'))
		if ( nativeLayerGroup in names ):
			self.metaData().setValue( 'groupIndex', names.index( nativeLayerGroup ) + 1 )	# preserve maxscripts 1-based indexing for the Maxscript Onion
			return True
		return False

	def _setNativeAtmospherics( self, nativeAtmospherics ):
		"""
			\remarks	implements the AbstractObjectGroup._setNativeAtmospherics method to set the inputed list of atmospherics
			\param		nativeAtmospherics	<list> [ <Py3dsMax.mxs.Atmospheric> nativeAtmospheric, .. ]
			\return		<bool> success
		"""
		atm 		= []
		unique_id 	= mxs.blurUtil.uniqueId

		# collect the id's for this layer
		for atmos in nativeAtmospherics:
			atm.append( unique_id( atmos ) )
		self.metaData().setValue( 'linkedAtmos', atm )

		# reset the id's on other layers
		for layer in self._scene.layers():
			if ( layer == self ):
				continue

			latm = list(layer.metaData().value( 'linkedAtmos' ))
			latm = [ i for i in latm if not i in atm ]
			layer.metaData().setValue( 'linkedAtmos', latm )

		return True

	def _setNativeFxs( self, nativeFxs ):
		"""
			\remarks	implements the AbstractObjectGroup._setNativeFxs method to set the inputed list of fxs
			\param		nativeFxs	<list> [ nativeFx, .. ]
			\return		<bool> success
		"""
		atm 		= []
		unique_id 	= mxs.blurUtil.uniqueId

		# collect the id's for this layer
		for atmos in nativeFxs:
			atm.append( unique_id( atmos ) )
		self.metaData().setValue( 'linkedFx', atm )
		return True

	def _setNativeWireColor( self, nativeColor ):
		"""
			\remarks	implements the AbstractSceneLayer._setNativeWireColor method to set the wirecolor for this layer instance
			\sa			setWireColor
			\param		nativeColor		<Py3dsMax.mxs.Color>
			\return		<bool> success
		"""
		self._nativePointer.wirecolor = nativeColor
		return True

	def _nativeWireColor( self ):
		"""
			\remarks	implements the AbstractSceneLayer._nativeWireColor method to return the wirecolor for this layer instance
			\sa			nativeColor
			\return		<Py3dsMax.mxs.Color> nativeColor || None
		"""
		return self._nativePointer.wirecolor

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def advancedAltMaterialStateAt( self, index ):
		"""
			\remarks	implements the AbstractSceneLayer.advancedAltMaterialStateAt method to return a mapping for the advanced alternate material status of a given alternate material
						slot
			\param		index	<int>
			\return		<dict> [ <int> baseMaterialId: (<cross3d.SceneMaterial> overrideMaterial, <bool> ignored), .. }
		"""
		data 				= self.metaData()
		altMaterialIndexes	= list(data.value( 'altMtlIndexes' ))
		baseMaterialIds		= list(data.value( 'baseMtlIds' ))
		baseMaterialNames	= list(data.value( 'baseMtlNames' ))
		overrideMtls		= list(data.value( 'overrideMtls' ))

		output = {}

		from cross3d import SceneMaterial

		# collect all the material overrides for the inputed alternate material index
		index += 1 # match maxscript 1-based array's
		for i, altMtlIndex in enumerate(altMaterialIndexes):
			# by compiliing a list of all the recroded materials for that index
			if ( altMtlIndex == index ):
				# determine the base material override
				nativeOverride = overrideMtls[i]
				if ( nativeOverride ):
					overrideMaterial 	= SceneMaterial( self.scene(), nativeOverride )
					ignoreOverride		= False
				else:
					overrideMaterial	= None
					ignoreOverride		= True

				output[baseMaterialIds[i]] = (overrideMaterial,ignoreOverride)

		return output

	def altMaterialFlags( self ):
		"""
			\remarks	implements the AbstractSceneLayer.altMaterialFlags method to return a list of material duplication flags for this layer
			\return		<list> [ <cross3d.constants.MaterialOverrideOptions>, .. ]
		"""
		if ( self._altMtlFlagsCache == None ):
			self._altMtlFlagsCache = []

			keepDisplacement 	= list(self.metaData().value( 'keepDisplacement' ))
			keepOpacity			= list(self.metaData().value( 'keepOpacity' ))

			from cross3d.constants import MaterialOverrideOptions
			for i in range( len( keepDisplacement ) ):
				flags = 0
				if ( keepDisplacement[i] ):
					flags |= MaterialOverrideOptions.KeepDisplacement
				if ( keepOpacity[i] ):
					flags |= MaterialOverrideOptions.KeepOpacity

				self._altMtlFlagsCache.append(flags)

		return self._altMtlFlagsCache

	def altPropSets( self ):
		"""
			\remarks	implements the AbstractSceneLayer.altPropSets method to retrive the alternate SceneObjectPropSet's for this layer
			\sa			altPropSetCount, altPropAt, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<list> [ <cross3d.SceneObjectPropSet>, .. ]
		"""
		if ( self._altPropCache == None ):
			from cross3d import SceneObjectPropSet
			cache 			= []
			data 			= self.metaData()
			altPropValues	= list(data.value('altPropValues'))
			altPropUsages	= list(data.value('altPropUsages'))
			altPropIds		= list(data.value('altPropIds'))
			scene			= self._scene
			processed		= []

			for i in range(len(altPropValues)):
				# If, for some reason, we have a mismatch between the number
				# of ids and the number of property sets, we can correct that
				# problem here and update the metadata for the layer.
				if (i + 1) > len(altPropIds):
					altPropIds.append(mxs.blurUtil.genUniqueId())
					data.setValue('altPropIds', altPropIds)
				# This is unusual, but there seem to be rare cases of layer
				# metadata being polluted with multiple entries for a propset.
				# This results in strange behavior in Onion, so we're just
				# going to filter out the dups here. <jbee>
				if altPropIds[i] in processed:
					continue
				altProp = SceneObjectPropSet( scene, None )
				altProp.setUniqueId( altPropIds[i] )
				altProp._setValueString( altPropValues[i] )
				altProp._setActiveString( altPropUsages[i] )
				cache.append(altProp)
				processed.append(altProp.uniqueId())
			self._altPropCache = cache
		return self._altPropCache

	def hasAdvancedAltMaterialStateAt( self, index ):
		"""
			\remarks	[abstract] return whether or not an advanced state for an alternate material has been defined for the inputed
						alternate material index
			\param		index	<int>
			\return		<bool> found
		"""
		return (index+1) in list(self.metaData().value('altMtlIndexes') )

	def isActive( self ):
		"""
			\remarks	implements the AbstractSceneLayer.isActive method to return whether or not this layer is currently active in the scene
			\sa			setActive
			\return		<bool> active
		"""
		return self._nativePointer.current

	def isFrozen( self ):
		"""
			\remarks	implements the AbstractSceneObjectGroup.isFrozen method to retrieve the group name for this object group instance
			\return		<bool> frozen
		"""
		return self._nativePointer.isfrozen

	def isHidden( self ):
		"""
			\remarks	implements the AbstractSceneObjectGroup.isHidden method to retrieve the group name for this object group instance
			\return		<bool> hidden
		"""
		return self._nativePointer.ishidden

	def isWorldLayer( self ):
		"""
			\remarks	implements the AbstractSceneLayer.isWorldLayer method to check if this layer is the root world layer or not
			\return		<bool> is world
		"""
		if hasattr(self._nativePointer, 'name'):
			return self._nativePointer.name == '0'
		else:
			return False

	def layerGroupOrder( self ):
		"""
			\remarks	implements the AbstractSceneLayer.layerGroupOrder method to return the sort order index for this layer within its group
			\sa			setLayerGroupOrder
			\return		<int> index
		"""
		return self.metaData().value( 'groupOrder' )

	def setDisplayName( self, name ):
		"""
			\remarks	implements the AbstractSceneLayer.setName method to set the layer display name for this layer instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		self._nativePointer.setname('')
		self._nativePointer.setname( str(name) )
		# Reset the metadata and requery it from the scene file.  That will
		# force an update of the name value and ensure we don't create a
		# disconnect between the metadata entry and the newly-renamed layer.
		self._metaData = None
		self.metaData()
		return

	def metaData( self ):
		if ( not self._metaData ):
			layerName 	= str(self.name())
			layerId		= self.uniqueId()

			# grab the cust attribute by the layer name
			root		= mxs.rootNode
			order		= 1
			count		= mxs.custAttributes.count( root )
			get_attr	= mxs.custAttributes.get
			is_prop		= mxs.isProperty

			metaData	= None

			for i in range(count):
				attr = get_attr( root, i + 1 )
				if ( str(attr.name).lower() == 'oniondata' ):
					# lookup the property
					if ((is_prop( attr, 'lnm' ) and layerName == attr.lnm) or attr.lid == layerId ):
						metaData = LayerMetaData(attr)
						if attr.lnm != layerName:
							metaData.setValue('layerName', str(self.name()))
						break

					# create a new one if necessary
					elif ( is_prop( attr, 'gi' ) and attr.gi == 1 ):
						order += 1

			# create new data if necessary
			if ( not metaData ):
				metaData = LayerMetaData.createUnique( root )

				# initialize some more data
				metaData.setValue( 'layerId', 	self.uniqueId() )
				metaData.setValue( 'layerName', str( self.name() ) )
				metaData.setValue( 'groupIndex', 1 )
				metaData.setValue( 'groupOrder', order )

			self._metaData = metaData

		return self._metaData

	def name( self ):
		"""
			\remarks	implements the AbstractSceneLayer.name method to retrieve the unique layer name for this layer
			\sa			name
			\return		<str> name
		"""
		if hasattr(self._nativePointer, 'name'):
			name = self._nativePointer.name
		else:
			return ''
		if ( name == '0' ):
			return 'World Layer'
		return name

	def refreshMetaData(self):
		""" Refreshes the current layer metadata.  If any new params are added,
		this will allow the new params to be ingested in already created
		metadata. Essentially, creates a new metadata object and stores all the
		properties into it.
		"""
		get_attr = mxs.custAttributes.get
		rem_attr = mxs.cutAttributes.delete
		root = mxs.rootNode
		count = mxs.custAttributes.count(root)
		mxsinst = ()
		for i in range(count, 0, -1):
			attr = get_attr(root,i)
			if str(attr.name).lower() == 'oniondata':
				layer = None
				# Only retrieve the current layers attribute
				if mxs.isproperty(attr, 'lnm') and attr.lnm == self.name():
					mxsinst = (i, attr)
					break
		if mxsinst:
			inst = mxsinst[0]
			oldmxs = mxsinst[1]
			# Create a new metadata object and copy all the old
			# mxs instance properties to the new one.  This will
			# retain all the information while allowing for
			# additional properties to be added later on.
			newMetaData = LayerMetaData.createUnique(root)
			for prop in mxs.getPropNames(oldmxs):
				propval = mxs.getproperty(oldmxs, prop)
				mxs.setproperty(newMetaData._mxsInstance, prop, propval)
			rem_attr(root, inst)
			LayerMetaData.register()
			self._metaData = newMetaData

	def remove( self, removeObjects = False ):
		"""
			\remarks	implements the AbstractSceneObjectGroup.remove method to remove the layer from the scene (objects included when desired)
			\param		removeObjects	<bool>	when true, the objects on the layer should be removed from the scene, otherwise
												only the layer should be removed
			\return		<bool> success
		"""
		my_layer	= self._nativePointer
		worldlayer 	= mxs.layerManager.getLayer(0)
		# cannot remove the world layer
		if ( my_layer == worldlayer ):
			return False

		# deactivate this layer since we cannot delete active layers
		self.setActive(False)

		# otherwise, collect the objects on this layer
		objects = mxs.pyhelper.getLayerNodes( my_layer )

		# determine what to do with the objects
		if ( objects ):
			# remove the objects from the scene
			if ( removeObjects ):
				mxs.delete( objects )

			# move the objects to the world layer
			else:
				addnode = worldlayer.addNode
				for obj in objects:
					addnode(obj)

		# remove this layer
		return mxs.layerManager.deleteLayerByName( my_layer.name )

	def removeAdvancedAltMaterialStateAt( self, index ):
		"""
			\remarks	implements the AbstractSceneLayer.clearAdvancedAltMaterialState method to remove the advanced state for the inputed
						alternate material index
			\param		index	<int>
			\return		<bool> success
		"""
		data 				= self.metaData()

		# collect the data
		altMaterialIndexes	= list(data.value( 'altMtlIndexes' ))
		baseMaterialIds		= list(data.value( 'baseMtlIds' ))
		baseMaterialNames	= list(data.value( 'baseMtlNames' ))
		overrideMtls		= list(data.value( 'overrideMtls' ))

		# make the index match maxscripts 1-based arrays
		index += 1

		# create the new data
		newAltMaterialIndexes	= []
		newBaseMaterialIds		= []
		newBaseMaterialNames	= []
		newOverrideMtls			= []

		# preserve other override's information
		for i, altMtlIndex in enumerate(altMaterialIndexes):
			# remove references to the current index
			if ( altMtlIndex == index ):
				continue

			# decrement the references to future indexes
			elif ( index < altMtlIndex ):
				altMtlIndex -= 1

			newAltMaterialIndexes.append( 	altMtlIndex )
			newBaseMaterialIds.append( 		baseMaterialIds[i] )
			newBaseMaterialNames.append( 	baseMaterialNames[i] )
			newOverrideMtls.append(			overrideMtls[i] )

		# record the data
		data.setValue( 'altMtlIndexes', 	newAltMaterialIndexes )
		data.setValue( 'baseMtlIds',		newBaseMaterialIds )
		data.setValue( 'baseMtlNames',		newBaseMaterialNames )
		data.setValue( 'overrideMtls',		newOverrideMtls )

		return True

	def removeAltMaterialAt( self, index ):
		"""
			\remarks	reimplement the AbstractSceneLayer.removeAltMaterialAt method to only allow the removal of a property set if there is more than 1 remaining
			\param		index	<int>
			\return		<bool> success
		"""
		if ( self.altMaterialCount() > 1 ):
			return AbstractSceneLayer.removeAltMaterialAt( self, index )
		return False

	def removeAltPropSetAt( self, index ):
		"""
			\remarks	reimplement the AbstractSceneLayer.removeAltPropSetAt method to only allow the removal of a property set if there is more than 1 remaining
			\param		index	<int>
			\return		<bool> success
		"""
		if ( self.altPropSetCount() > 1 ):
			return AbstractSceneLayer.removeAltPropSetAt( self, index )
		return False

	def saveCurrentLightProperty(self, propSet):
		for obj in self._nativeObjects():
			if mxs.classOf(obj) == mxs.VRayLight:
				if propSet.value('primaryVisibility'):
					so = SceneObject(self._scene, obj)
					so.userProps()['previousInvisibleState'] = obj.invisible
					obj.invisible = True

	def setActive( self, state ):
		"""
			\remarks	implements the AbstractSceneLayer.setActive method to mark this layer as the active scene layer
			\sa			isActive
			\param		state	<bool>
			\return		<bool> success
		"""
		if ( state ):
			self._nativePointer.current = True
		else:
			mxs.layerManager.getLayer(0).current = True

		return self._nativePointer.current

	def setAdvancedAltMaterialStateAt( self, index, altMaterialState ):
		"""
			\remarks	implements AbstractSceneLayer.setAdvancedAltMaterialStateAt method to set a mapping for the advanced alternate material status of a given alternate material
						slot
			\param		index	<int>
			\param		<dict> [ <int> baseMaterialId: (<cross3d.SceneMaterial> override, <bool> ignored), .. }
			\return		<bool> success
		"""
		data = self.metaData()

		# grab the old data
		altMaterialIndexes	= list(data.value( 'altMtlIndexes' ))
		baseMaterialIds		= list(data.value( 'baseMtlIds' ))
		baseMaterialNames	= list(data.value( 'baseMtlNames' ))
		overrideMtls		= list(data.value( 'overrideMtls' ))

		# create the new data
		newAltMaterialIndexes	= []
		newBaseMaterialIds		= []
		newBaseMaterialNames	= []
		newOverrideMtls			= []

		# preserve other override's information
		index += 1 # match maxscript 1-based array's
		for i, altMtlIndex in enumerate(altMaterialIndexes):
			if ( altMtlIndex != index ):
				newAltMaterialIndexes.append( 	altMaterialIndexes[i] )
				newBaseMaterialIds.append( 		baseMaterialIds[i] )
				newBaseMaterialNames.append( 	baseMaterialNames[i] )
				newOverrideMtls.append( 		overrideMtls[i] )

		# record new alternate material information
		for baseMaterialId, state in altMaterialState.items():
			overrideMtl, ignoreMtl = state
			if ( not (ignoreMtl or overrideMtl) ):
				continue

			elif ( overrideMtl ):
				overrideMtl = overrideMtl.nativePointer()

			newAltMaterialIndexes.append( index )
			newBaseMaterialIds.append( baseMaterialId )
			newBaseMaterialNames.append( '' )
			newOverrideMtls.append( overrideMtl )

		# record the data
		data.setValue( 'altMtlIndexes', 	newAltMaterialIndexes )
		data.setValue( 'baseMtlIds',		newBaseMaterialIds )
		data.setValue( 'baseMtlNames',		newBaseMaterialNames )
		data.setValue( 'overrideMtls',		newOverrideMtls )

		return True

	def setAltMaterialFlags( self, flags ):
		"""
			\remarks	implements the AbstractSceneLayer.setAltMaterialFlags method to set the alternate material flags for this instance
			\param		flags	<list> [ <cross3d.constants.MaterialOverrideOptions>
			\return		<bool> success
		"""

		keepDisp = []
		keepOpac = []
		keepBump = []

		from cross3d.constants import MaterialOverrideOptions
		for flag in flags:
			keepDisp.append( (flag & MaterialOverrideOptions.KeepDisplacement) != 0 )
			keepOpac.append( (flag & MaterialOverrideOptions.KeepOpacity) != 0 )
			keepBump.append( (flag & MaterialOverrideOptions.KeepBump) != 0)

		data = self.metaData()
		data.setValue( 'keepDisplacement', 	keepDisp )
		data.setValue( 'keepOpacity',	 	keepOpac )
		data.setValue( 'keepBump',			keepBump )
		self._altMtlFlagsCache = flags
		return True

	def setAltPropSetAt( self, index, propSet ):
		"""
			\remarks	implements the AbstractSceneLayer.setAltPropSetAt method to set the alternate object property set at the inputed index
			\sa			altPropSetCount, altPropSetAt, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSets,
						setCurrentAltPropSetIndex
			\return		<bool> success
		"""
		altPropSets = self.altPropSets()
		if ( 0 <= index and index < len( altPropSets ) ):
			altPropSets[index] = propSet
			return self.setAltPropSets(altPropSets)
		return False

	def setAltPropSets( self, propSets ):
		"""
			\remarks	implements the AbstractSceneLayer.setAltPropSets method to set the alternate object property set list for this layer
			\sa			altPropSetCount, altPropSetAt, altPropSets, currentAltPropSet, currentAltPropSetIndex, setAltPropSetAt,
						setCurrentAltPropSetIndex
			\return		<bool> success
		"""
		# set the set values
		altPropValues 	= []
		altPropUsages 	= []
		altPropIds		= []

		# use blank prop strings for empty sets
		from cross3d import SceneObjectPropSet
		blank 		= SceneObjectPropSet( self._scene, None )
		blankValues = blank._valueString()
		blankUsages = blank._activeString()

		newSets = []
		for propSet in propSets:
			if ( propSet ):
				altPropValues.append( propSet._valueString() )
				altPropUsages.append( propSet._activeString() )
				altPropIds.append( propSet.uniqueId() )
				newSets.append( propSet )
			else:
				altPropValues.append( blankValues )
				altPropUsages.append( blankUsages )
				altPropIds.append( 0 )
				newSets.append( SceneObjectPropSet( self._scene, None ) )

		data = self.metaData()
		data.setValue( 'altPropValues', altPropValues )
		data.setValue( 'altPropUsages', altPropUsages )
		data.setValue( 'altPropIds', altPropIds )

		self._altPropCache = newSets
		return True

	def setCurrentAltMaterialIndex( self, index ):
		"""
			\remarks	reimplements the AbstractSceneLayer.setCurrentAltMaterialIndex method to set the alternate property index, and record the change
						to the Studiomax meta data
			\sa			AbstractSceneLayer.setCurrentAltMaterialIndex
			\param		index	<int>
			\return		<bool> changed
		"""
		if ( AbstractSceneLayer.setCurrentAltMaterialIndex( self, index ) ):
			self.metaData().setValue( 'currentAltMtlIndex', index + 1 )
			return True
		return False

	def setCurrentAltPropSetIndex( self, index ):
		"""
			\remarks	reimplements the AbstractSceneLayer.setCurrentAltPropSetIndex method to set the alternate property index, and record the change
						to the Studiomax meta data
			\sa			AbstractSceneLayer.setCurrentAltPropSetIndex
			\param		index	<int>
			\return		<bool> changed
		"""
		if ( AbstractSceneLayer.setCurrentAltPropSetIndex( self, index ) ):
			self.metaData().setValue( 'currentAltPropIndex', index + 1 )
			return True
		return False

	def setLayerGroupOrder( self, index ):
		"""
			\remarks	implements the AbstractSeneLayer.setLayerGroupOrder method to set the sort index for this layer group to the inputed index
			\sa			layerGroupOrder
			\param		index	<int>
			\return		<bool> changed
		"""
		self.metaData().setValue( 'groupOrder', index + 1 )
		return True

	def setFrozen(self, state, affectObjects=False):
		"""
			\remarks	reimplements the AbstractSceneLayer.setFrozen method to set the frozen state for this layer
			\return		<bool> success
		"""
		self._nativePointer.isfrozen = state

		if affectObjects:
			# sync object frozen properties
			for obj in self._nativeObjects():
				obj.isfrozen = state

		return True

	def setHidden(self, state, options=None, affectObjects=False):
		"""
			\remarks	reimplements the AbstractSceneLayer.setHidden method to set the hidden state for this layer
			\return		<bool> success
		"""
		self._nativePointer.ishidden = state

		if affectObjects:
			# update the objects on this layer
			nativeObjects = self._nativeObjects()
			if ( state ):
				mxs.hide( nativeObjects )
			else:
				mxs.unhide( nativeObjects )

			# toggle visible rendering options
			self._scene._toggleNativeVisibleState(nativeObjects, options)

			# update the atmospherics on this layer
			for atmos in self.atmospherics():
				atmos.setEnabled( not state )

			# update the fx instances on this layer
			for fx in self.fxs():
				fx.setEnabled( not state )

		return True

	def setUniqueId( self, uniqueId ):
		"""
			\remarks	implements the AbstractSceneLayer.setUniqueId method to set the unique layer id for this layer instance
			\sa			uniqueId
			\param		uniqueId		<int>
			\return		<bool> success
		"""
		mxs.blurUtil.setUniqueId( self._nativePointer.layerAsRefTarg, uniqueId )
		return True

	def uniqueId( self ):
		"""
			\remarks	implements the AbstractSceneLayer.uniqueId method to retrieve the unique layer id for this layer instance
			\sa			setUniqueId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer.layerAsRefTarg )

# register the symbol
cross3d.registerSymbol( 'SceneLayer', StudiomaxSceneLayer )
