##
#	\namespace	blur3d.api.abstract.abstractscenelayergroup
#
#	\remarks	The AbstractSceneLayerGroup provides a cross-application interface to 3d scene layer's and their interaction
#				This class will provide the base implementation and definition of methods that will need to be re-implemented
#				to hanel per-application usage
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

class AbstractSceneLayerGroup:
	def __eq__( self, other ):
		"""
			\remarks	determines whether one SceneLayerGroup instance is equal to another by comparing the pointers to their native group pointers
			\param		other	<variant>
			\return		<bool> success
		"""
		if ( isinstance( other, AbstractSceneLayerGroup ) ):
			return self._nativePointer == other._nativePointer
		return False
		
	def __init__( self, scene, nativeLayerGroup ):
		# define custom properties
		self._scene					= scene
		self._nativePointer 		= nativeLayerGroup
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _addNativeLayers( self, nativeLayers ):
		"""
			\remarks	[abstract]	add the native layers to the layer group
			\sa			addLayers, addSelection
			\param		nativeLayers	<list> [ <variant> nativeLayer, .. ]
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _clearNativeLayers( self ):
		"""
			\remarks	[abstract] clear the native layers from this layer
			\sa			clearLayers
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def _nativeLayers( self ):
		"""
			\remarks	[abstract] return a list of the native layers that are currently on this layer group
			\sa			layers
			\return		<list> [ <variant> nativeLayers, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _nativeObjects( self ):
		"""
			\remarks	[abstract] return a list of all the native objects that are encompassed on this layer group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def addLayers( self, layers ):
		"""
			\remarks	add the layers to this layer group
			\sa			addSelection, _addNativeLayers
			\param		layers		<list> [ <blur3d.api.SceneLayer>, .. ]
			\return		<bool> success
		"""
		return self._addNativeLayers( [ layer.nativeLayer() for layer in layers ] )
	
	def deselect( self ):
		"""
			\remarks	deselects the layers on this layer from the scene
			\sa			select, setSelected
			\return		<bool> success
		"""
		return self.setSelected(False)
	
	def freeze( self ):
		"""
			\remarks	freezes (locks) the layers on this layer in the scene
			\sa			setFrozen, unfreeze
			\return		<bool> success
		"""
		return self.setFrozen(True)
	
	def groupOrder( self ):
		"""
			\remarks	[abstract] return the order for this layer group
			\return		<int> order
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return -1
	
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
	
	def hide( self ):
		"""
			\remarks	hides the layers on this layer in the scene
			\sa			setHidden, unhide
			\return		<bool> success
		"""
		return self.setHidden( True )
	
	def isEmpty( self ):
		"""
			\remarks	returns whether or not this layer is empty (contains no chidren)
			\sa			_nativeLayers
			\return		<bool> empty
		"""
		return len( self._nativeLayers() ) == 0
	
	def isOpen( self ):
		"""
			\remarks	[abstract] return whether or not the layer group is open
			\return		<bool> open
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def groupName( self ):
		"""
			\remarks	[abstract] retrieve the unique layer name for this layer
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return ''
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native object that is wrapped
			\return		<variant> nativeLayer
		"""
		return self._nativePointer
	
	def layers( self ):
		"""
			\remarks	returns the SceneLayer's that are associated with this layer
			\return		<list> [ <blur3d.api.SceneLayer>, .. ]
		"""
		from blur3d.api import SceneLayer
		return [ SceneLayer( self._scene, lay ) for lay in self._nativeLayers() ]
	
	def objects( self ):
		"""
			\remarks	return a list of the objects that are part of this layer group
			\return		<list> [ <blur3d.api.SceneObject>, .. ]
		"""
		from blur3d.api import SceneObject
		return [ SceneObject( self._scene, obj ) for obj in self._nativeObjects() ]
	
	def remove( self, removeLayers = False, removeObjects = False ):
		"""
			\remarks	[abstract] remove the layer from the scene (layers included when desired)
			\param		removeLayers	<bool>	when true, the layers in the layer group should be removed from the scene, otherwise
												only the layer group should be removed
			\param		removeObjects	<bool>	if removeLayers is true, when removeObjects is true, the objects on the layers in the 
												layer group should be removed from the scene
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this layer is a member of
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def select( self ):
		"""
			\remarks	selects the items on this layer
			\sa			deselect, setSelected
			\return		<bool> success
		"""
		return self.setSelected(True)
	
	def setFrozen( self, state ):
		"""
			\remarks	set the frozen (locked) state for the layers in this layer group
			\sa			freeze, unfreeze, _nativeLayers, blur3d.api.Scene._freezeNativeLayers
			\param		state	<bool>
			\return		<bool> success
		"""
		for layer in self.layers():
			layer.setFrozen( state )
		return True
	
	def setGroupName( self, layerName ):
		"""
			\remarks	[abstract] set the name for this layer group instance
			\sa			layerName
			\param		layerName	<str>
			\return		<bool> changed
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setGroupOrder( self, groupOrder ):
		"""
			\remarks	[abstract] set the order number for this group instance
			\sa			groupOrder
			\param		groupOrder	<int>
			\return		<bool> changed
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setHidden( self, state ):
		"""
			\remarks	set the hidden state for the layers on this layer
			\sa			hide, unhide, _nativeObjets, blur3d.api.Scene._hideNativeLayers
			\param		state	<bool>
			\return		<bool> success
		"""
		for layer in self.layers():
			layer.setHidden( state )
		return True
		
	def setOpen( self, state ):
		"""
			\remarks	[abstract] set whether or not the layer group is open
			\param		state	<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setSelected( self, state ):
		"""
			\remarks	sets the selected state of the layers on this layer
			\sa			deselect, setSelected, _nativeLayers, blur3d.api.Scene.setSelection
			\param		state	<bool>
			\return		<bool> success
		"""
		for layer in self.layers():
			layer.setSelected( state )
		return True
	
	def unhide( self ):
		"""
			\remarks	unhides the layers in this layer group
			\sa			hide, setHidden
			\return		<bool> success
		"""
		return self.setHidden(False)
	
	def unfreeze( self ):
		"""
			\remarks	unfreezes the layers in this layer group
			\sa			freeze, setFrozen
			\return		<bool> success
		"""
		return self.setFrozen(False)


# register the symbol
from blur3d import api
api.registerSymbol( 'SceneLayerGroup', AbstractSceneLayerGroup, ifNotFound = True )