##
#	\namespace	blur3d.api.abstract.abstractsceneobjectgroup
#
#	\remarks	The AbstractSceneObjectGroup class provides an interface for working on sets of SceneObject's as a singular group
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d.api import SceneWrapper

class AbstractSceneObjectGroup( SceneWrapper ):
	def __init__( self, scene, nativeGroup ):
		SceneWrapper.__init__( self, scene, nativeGroup )
		
		# define custom properties
		self._materialOverride				= None			# blur3d.api.SceneMaterial 					- material to be used as the override material for the objects in this group
		self._materialOverrideFlags			= 0				# blur3d.constants.MaterialOverrideOptions		- options to be used when overriding materials
		self._materialOverrideAdvancedState = {}			# <dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		self._propSetOverride				= None			# blur3d.api.SceneObjectPropSet				- property set to be used as the override properties for the objects in this group
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _addNativeAtmospherics( self, nativeAtmospherics ):
		"""
			\remarks	[abstract] add the native atmospherics to the object group
			\sa			addAtmospherics
			\param		nativeAtmospherics	<list> [ <variant> nativeAtmospheric, .. ]
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _addNativeObjects( self, nativeObjects ):
		"""
			\remarks	[abstract]	add the native objects to the object group
			\sa			addObjects, addSelection
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _clearNativeMaterialOverride( self ):
		"""
			\remarks	[virtual] clear the native objects of any material overrides for this group
			\sa			blur3d.api.Scene._clearNativeMaterialOverride
			\return		<bool> success
		"""
		return self._scene._clearNativeMaterialOverride( self._nativeObjects() )
	
	def _clearNativePropSetOverride( self ):
		"""
			\remarks	[virtual] clear the native objects of any property set overrides for this group
			\sa			blur3d.api.Scene._clearNativePropSetOverride
			\return		<bool> success
		"""
		return self._scene._clearNativePropSetOverride( self._nativeObjects() )
	
	def _nativeAtmospherics( self ):
		"""
			\remarks	[abstract] return a list of the atmospherics that are associated with this object group
			\sa			atmospherics
			\return		<list> [ <variant> nativeAtmospheric, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeObjects( self ):
		"""
			\remarks	[abstract] return a list of the native objects that are currently on this group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeMaterials( self ):
		"""
			\remarks	[abstract] return a list of all the native materials that are contained within this object group
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeMaterialOverride( self ):
		"""
			\remarks	[abstract] return the current override material for this object group
			\return		<variant> nativeMaterial || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _setNativeAtmospherics( self, nativeAtmospherics ):
		"""
			\remarks	[abstract] set the linked atmopherics to this object group to the inputed list of atmospherics
			\param		nativeAtmospherics	<list> [ <variant> nativeAtmospheric, .. ]
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _setNativeMaterialOverride( self, nativeMaterial, options = -1, advancedState = None ):
		"""
			\remarks	[virtual] set the current override materials for this object group
			\sa			blur3d.api.Scene._setNativeMaterialOverride
			\param		nativeMaterial 	<variant> || None
			\param		options			<blur3d.constants.MaterialOverrideOptions>
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
			\return		<bool> success
		"""
		if ( options == -1 ):
			options = self.materialOverrideFlags()
		else:
			self.setMaterialOverrideFlags(options)
		
		if ( advancedState == None ):
			advancedState = self.materialOverrideAdvancedState()
		else:
			self.setMaterialOverrideAdvancedState( advancedState )
			
		return self._scene._setNativeMaterialOverride( self._nativeObjects(), nativeMaterial, options = options, advancedState = advancedState )
	
	def _setNativePropSetOverride( self, nativePropSet ):
		"""
			\remarks	[virtual] set the current override property set for this object group
			\sa			blur3d.api.Scene._setNativePropSetOverride
			\param		nativePropSet 	<variant> || None
			\return		<bool> success
		"""
		if ( nativePropSet ):
			return self._scene._setNativePropSetOverride( self._nativeObjects(), nativePropSet )
		else:
			return self._scene._clearNativePropSetOverride( self._nativeObjects() )
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def addAtmospherics( self, atmospherics ):
		"""
			\remarks	add the atmospherics to this object group
			\sa			_addNativeAtmospherics
			\param		atmospherics <list> [ <blur3d.api.SceneAtmospheric>, .. ]
			\return		<bool> success
		"""
		return self._addNativeAtmospherics( [ atmos.nativePointer() for atmos in atmospherics ] )
	
	def addObjects( self, objects ):
		"""
			\remarks	add the objects to this object group
			\sa			addSelection, _addNativeObjects
			\param		objects		<list> [ <blur3d.api.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._addNativeObjects( [ object.nativePointer() for object in objects ] )
	
	def addSelection( self ):
		"""
			\remarks	add the selected scene objects to this object group
			\sa			addObjects, _addNativeObjects
			\return		<bool> success
		"""
		return self._addNativeObjects( self._scene._nativeSelection() )
	
	def atmospherics( self ):
		"""
			\remarks	return a list of the atmospherics that are part of this object group
			\sa			_nativeAtmospherics
			\return		<list> [ <blur3d.api.SceneAtmospheric>, .. ]
		"""
		from blur3d.api import SceneAtmospheric
		return [ SceneAtmospheric( self._scene, atmos ) for atmos in self._nativeAtmospherics() ]
	
	def clearMaterialOverride( self ):
		"""
			\remarks	clears the current material overrides from this object group's objects
			\return		<bool> success
		"""
		return self._clearNativeMaterialOverride()
	
	def clearMaterialOverrideFlags( self ):
		"""
			\remarks	return whether or not the inputed flag is set in the override options
			\sa			hasMaterialOverrideFlag, materialOverrideFlags, setMaterialOverrideFlag, setMaterialOverrideFlags
			\return		<bool> success
		"""
		self._materialOverrideFlags = 0
		return True
	
	def clearPropSetOverride( self ):
		"""
			\remarks	clears the current prop set override from this object group's objects
			\return		<bool> success
		"""
		return self._clearNativePropSetOverride()
	
	def deselect( self ):
		"""
			\remarks	deselects the objects on this object group from the scene
			\sa			select, setSelected
			\return		<bool> success
		"""
		return self.setSelected(False)
	
	def freeze( self ):
		"""
			\remarks	freezes (locks) the objects on this object group in the scene
			\sa			setFrozen, unfreeze
			\return		<bool> success
		"""
		return self.setFrozen(True)
	
	def hasMaterialOverrideFlag( self, flag ):
		"""
			\remarks	return whether or not the inputed flag is set in the override options
			\sa			clearMaterialOverrideFlags, materialOverrideFlags, setMaterialOverrideFlag, setMaterialOverrideFlags
			\param		flag	<blur3d.constants.MaterialOverrideOptions>
			\return		<bool> exists
		"""
		return (self._materialOverrideFlags & flag) != 0
	
	def hide( self ):
		"""
			\remarks	hides the objects on this object group in the scene
			\sa			setHidden, unhide
			\return		<bool> success
		"""
		return self.setHidden( True )
	
	def isEmpty( self ):
		"""
			\remarks	returns whether or not this object group is empty (contains no chidren)
			\sa			_nativeObjects
			\return		<bool> empty
		"""
		return len( self._nativeObjects() ) == 0
	
	def isFrozen( self ):
		"""
			\remarks	[abstract] retrieve the group name for this object group instance
			\return		<bool> frozen
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	def isHidden( self ):
		"""
			\remarks	[abstract] retrieve the group name for this object group instance
			\return		<bool> hidden
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def isVisible( self ):
		"""
			\remarks	return whether or not this object group is visible
			\sa			isHidden
			\return		<bool> visible
		"""
		return not self.isHidden()
	
	def isolate( self ):
		"""
			\remarks	isolates the objects in this group in the scene
			\sa			AbstractScene._isolateNativeObjects
			\return		<bool> success
		"""
		return self._scene._isolateNativeObjects( self._nativeObjects() )
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native object that is wrapped
			\return		<variant> nativeLayer
		"""
		return self._nativePointer
	
	def objects( self ):
		"""
			\remarks	returns the SceneObject's that are associated with this object group
			\return		<list> [ <blur3d.api.SceneObject>, .. ]
		"""
		from blur3d.api import SceneObject
		return [ SceneObject( self._scene, obj ) for obj in self._nativeObjects() ]
	
	def materials( self ):
		"""
			\remarks	return a list of all the materials contained within this object group
			\sa			_nativeMaterials
			\return		<list> [ <blur3d.api.SceneMaterial>, .. ]
		"""
		from blur3d.api import SceneMaterial
		return [ SceneMaterial( self._scene, mtl ) for mtl in self._nativeMaterials() ]
	
	def materialOverride( self ):
		"""
			\remarks	return the current override material for this object set
			\return		<blur3d.api.SceneMaterial> || None
		"""
		nativeMaterial = self._nativeMaterialOverride()
		if ( nativeMaterial ):
			from blur3d.api import SceneMaterial
			return SceneMaterial( self.scene(), nativeMaterial )
		return None
	
	def materialOverrideAdvancedState( self ):
		"""
			\remarks	return the current advanced material override state that the object group is in
			\return		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		"""
		return self._materialOverrideAdvancedState
	
	def materialOverrideFlags( self ):
		"""
			\remarks	return the duplication flags for the override material
			\sa			clearMaterialOverrideFlags, hasMaterialOverrideFlag, setMaterialOverrideFlag, setMaterialOverrideFlags
			\return		<blur3d.constants.MaterialOverrideOptions>
		"""
		return self._materialOverrideFlags
	
	def propSetOverride( self ):
		"""
			\remarks	return the current override prop set for this object set
			\return		<blur3d.api.SceneObjectPropSet> || None
		"""
		from blur3d.api import ScenePropSet
		nativePropSet = self._nativePropSetOverride()
		if ( nativePropSet and not isinstance( nativePropSet, ScenePropSet ) ):
			return ScenePropSet( self.scene(), nativePropSet )
		return nativePropSet
	
	def remove( self, removeObjects = False ):
		"""
			\remarks	[abstract] remove the object group from the scene (objects included when desired)
			\param		removeObjects	<bool>	when true, the objects on the object group should be removed from the scene, otherwise
												only the object group should be removed
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def select( self ):
		"""
			\remarks	selects the items on this object group
			\sa			deselect, setSelected
			\return		<bool> success
		"""
		return self.setSelected(True)
	
	def setActive( self, state ):
		"""
			\remarks	[abstract] mark this object group as the active scene object group
			\sa			isActive
			\param		state	<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setMaterialOverride( self, material, options = -1, advancedState = None ):
		"""
			\remarks	set the override material on the objects for this set
			\sa			_setNativeMaterialOverride
			\param		material		<blur3d.api.SceneMaterial> || None
			\param		options			<blur3d.constants.MaterialOverrideOptions>
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
			\return		<bool> success
		"""
		nativeMaterial = None
		if ( material ):
			nativeMaterial = material.nativePointer()
		
		if ( options == -1 ):
			options = self.materialOverrideFlags()
			
		return self._setNativeMaterialOverride( nativeMaterial, options = options, advancedState = advancedState )
		
	def setMaterialOverrideFlag( self, flag, state = True ):
		"""
			\remarks	set the inputed flag on or off based on the state
			\sa			clearMaterialOverrideFlags, hasMaterialOverrideFlag, materialOverrideFlags, setMaterialOverrideFlags
			\param		flag	<blur3d.constants.MaterialOverrideOptions>
			\param		state	<bool>
			\return		<bool> success
		"""
		if ( state ):
			self._materialOverrideFlags |= flag
		else:
			self._materialOverrideFlags ^= flag
		return True
	
	def setMaterialOverrideFlags( self, flags ):
		"""
			\remarks	set all of the duplication flags for override materials
			\sa			clearMaterialOverrideFlags, hasMaterialOverrideFlag, materialOverrideFlags, setMaterialOverrideFlag
			\param		flags	<blur3d.constants.MaterialOverrideOptions>
			\return		<bool> success
		"""
		self._materialOverrideFlags = flags
		return True
	
	def setMaterialOverrideAdvancedState( self, advancedState ):
		"""
			\remarks	set an advanced state for this object group to be in
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
			\return		<bool> success
		"""
		self._materialOverrideAdvancedState = advancedState
	
	def setAtmospherics( self, atmospherics ):
		"""
			\remarks	sets the atmospherics that are associated with this object group to the inputed list of atmospherics
			\sa			atmospherics, _setNativeAtmospherics
			\param		atmospherics	<list> [ <blur3d.api.SceneAtmospheric>, .. ]
			\return		<bool> success
		"""
		return self._setNativeAtmospherics( [ atmos.nativePointer() for atmos in atmospherics ] )
	
	def setPropSetOverride( self, propSet ):
		"""
			\remarks	set the override properties on the objects that are a part of this object group
			\param		propSet		<blur3d.api.SceneObjectPropSet>
			\return		<bool> success
		"""
		nativePropSet = None
		if ( propSet ):
			nativePropSet = propSet.nativePointer()
		
		return self._setNativePropSetOverride( nativePropSet )
	
	def setFrozen( self, state ):
		"""
			\remarks	set the frozen (locked) state for the objects on this object group
			\sa			freeze, unfreeze, _nativeObjects, blur3d.api.Scene._freezeNativeObjects
			\param		state	<bool>
			\return		<bool> success
		"""
		return self._scene._freezeNativeObjects( self._nativeObjects(), state )
	
	def setHidden( self, state, options = None ):
		"""
			\remarks	set the hidden state for the objects on this object group
			\sa			hide, unhide, _nativeObjets, blur3d.api.Scene._hideNativeObjects
			\param		state		<bool>
			\param		options		<blur3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		objs = self._nativeObjects()
		self._scene._hideNativeObjects( objs, state )
		return True
		
	def setSelected( self, state ):
		"""
			\remarks	sets the selected state of the objects on this object group
			\sa			deselect, setSelected, _nativeObjects, blur3d.api.Scene.setSelection
			\param		state	<bool>
			\return		<bool> success
		"""
		return self._scene._setNativeSelection( self._nativeObjects() )
	
	def setVisible( self, state ):
		"""
			\remarks	set whether or not this object group is visible
			\param		state	<bool>
			\return		success
		"""
		return self.setHidden( not state )
	
	def unhide( self ):
		"""
			\remarks	unhides the objects on this object group
			\sa			hide, setHidden
			\return		<bool> success
		"""
		return self.setHidden(False)
	
	def unfreeze( self ):
		"""
			\remarks	unfreezes the objects on this object group
			\sa			freeze, setFrozen
			\return		<bool> success
		"""
		return self.setFrozen(False)


# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObjectGroup', AbstractSceneObjectGroup, ifNotFound = True )