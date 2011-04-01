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

from blur3d 	import abstractmethod
from blur3d.api import SceneWrapper

class AbstractSceneLayerGroup( SceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _addNativeLayers( self, nativeLayers ):
		"""
			\remarks	add the native layers to the layer group
			\sa			addLayers, addSelection
			\param		nativeLayers	<list> [ <variant> nativeLayer, .. ]
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _clearNativeLayers( self ):
		"""
			\remarks	clear the native layers from this layer
			\sa			clearLayers
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _nativeLayers( self ):
		"""
			\remarks	return a list of the native layers that are currently on this layer group
			\sa			layers
			\return		<list> [ <variant> nativeLayers, .. ]
		"""
		return []
	
	@abstractmethod
	def _nativeObjects( self ):
		"""
			\remarks	return a list of all the native objects that are encompassed on this layer group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
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
	
	@abstractmethod
	def groupOrder( self ):
		"""
			\remarks	return the order for this layer group
			\return		<int> order
		"""
		return -1
	
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
	
	@abstractmethod
	def isOpen( self ):
		"""
			\remarks	return whether or not the layer group is open
			\return		<bool> open
		"""
		return False
	
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
	
	@abstractmethod
	def remove( self, removeLayers = False, removeObjects = False ):
		"""
			\remarks	remove the layer from the scene (layers included when desired)
			\param		removeLayers	<bool>	when true, the layers in the layer group should be removed from the scene, otherwise
												only the layer group should be removed
			\param		removeObjects	<bool>	if removeLayers is true, when removeObjects is true, the objects on the layers in the 
												layer group should be removed from the scene
			\return		<bool> success
		"""
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
	
	@abstractmethod
	def setGroupOrder( self, groupOrder ):
		"""
			\remarks	set the order number for this group instance
			\sa			groupOrder
			\param		groupOrder	<int>
			\return		<bool> changed
		"""
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
		
	@abstractmethod
	def setOpen( self, state ):
		"""
			\remarks	set whether or not the layer group is open
			\param		state	<bool>
			\return		<bool> success
		"""
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