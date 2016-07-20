##
#	\namespace	cross3d.abstract.abstractscenelayergroup
#
#	\remarks	The AbstractSceneLayerGroup provides a cross-application interface to 3d scene layer's and their interaction
#				This class will provide the base implementation and definition of methods that will need to be re-implemented
#				to hanel per-application usage
#
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import SceneWrapper, abstractmethod

class AbstractSceneLayerGroup(SceneWrapper):

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	@abstractmethod
	def _addNativeLayers(self, nativeLayers):
		"""
			\remarks	add the native layers to the layer group
			\sa			addLayers, addSelection
			\param		nativeLayers	<list> [ <variant> nativeLayer, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _clearNativeLayers(self):
		"""
			\remarks	clear the native layers from this layer
			\sa			clearLayers
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _nativeLayers(self):
		"""
			\remarks	return a list of the native layers that are currently on this layer group
			\sa			layers
			\return		<list> [ <variant> nativeLayers, .. ]
		"""
		return []

	@abstractmethod
	def _nativeObjects(self):
		"""
			\remarks	return a list of all the native objects that are encompassed on this layer group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return []

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def addLayers(self, layers):
		"""Add the layers to this layer group

		:param layers: list of :class:`cross3d.SceneLayer`'s

		"""
		return self._addNativeLayers([ layer.nativePointer() for layer in layers ])

	def deselect(self):
		"""Deselects the layers on this layer from the scene

		"""
		return self.setSelected(False)

	def freeze(self, affectObjects=False):
		"""Freezes (locks) the layers on this layer in the scene

		"""
		return self.setFrozen(True, affectObjects=affectObjects)

	@abstractmethod
	def groupOrder(self):
		"""Return the order for this layer group

		"""
		return -1

	def hide(self, options=None, affectObjects=False):
		"""Hides the layers on this layer in the scene

		"""
		return self.setHidden(True, options=options, affectObjects=affectObjects)

	def isEmpty(self):
		"""Returns whether or not this layer is empty (contains no chidren)

		"""
		return len(self._nativeLayers()) == 0

	@abstractmethod
	def isOpen(self):
		"""Return whether or not the layer group is open

		"""
		return False

	def layers(self):
		"""Returns the SceneLayer's that are associated with this layer

		:return: list of :class:`cross3d.SceneLayer`'s

		"""
		from cross3d import SceneLayer
		return [ SceneLayer(self._scene, lay) for lay in self._nativeLayers() ]

	def objects(self):
		"""Return a list of the objects that are part of this layer group

		:return: list of :class:`cross3d.SceneObject`'s

		"""
		from cross3d import SceneObject
		return [ SceneObject(self._scene, obj) for obj in self._nativeObjects() ]

	@abstractmethod
	def remove(self, removeLayers=False, removeObjects=False):
		"""Remove the layer from the scene (layers included when desired)

		:param removeLayers: If true, the layers in the layer group should
		                    be removed from the scene, otherwise only the
		                    layer group should be removed
		:type removeLayers: bool
		:param removeObjects: If removeLayers is true, when removeObjects
							is true, the objects on the layers in the
							layer group should be removed from the scene

		"""
		return False

	def scene(self):
		"""Return the scene instance that this layer is a member of

		:return: :class:`cross3d.Scene`

		"""
		return self._scene

	def select(self):
		"""Selects the items on this layer

		"""
		return self.setSelected(True)

	def setFrozen(self, state, affectObjects=False):
		"""Set the frozen (locked) state for the layers in this layer group

		"""
		for layer in self.layers():
			layer.setFrozen(state, affectObjects=affectObjects)
		return True

	@abstractmethod
	def setGroupOrder(self, groupOrder):
		"""Set the order number for this group instance

		"""
		return False

	def setHidden(self, state, options=None, affectObjects=False):
		"""Set the hidden state for the layers on this layer

		"""
		for layer in self.layers():
			layer.setHidden(state, options=options, affectObjects=affectObjects)
		return True

	@abstractmethod
	def setOpen(self, state):
		"""Set whether or not the layer group is open

		"""
		return False

	def setSelected(self, state):
		"""Sets the selected state of the layers on this layer

		"""
		for layer in self.layers():
			layer.setSelected(state)
		return True

	@abstractmethod
	def sortLayers(self, key=None):
		"""
		Sorts the layers within the group.  The layers will be sorted
		alphabetically unless specified otherwise by a key.
		"""
		return False

	def unhide(self, options=None, affectObjects=False):
		"""Unhides the layers in this layer group

		"""
		return self.setHidden(False, options=options, affectObjects=affectObjects)

	def unfreeze(self, affectObjects=False):
		"""Unfreezes the layers in this layer group

		"""
		return self.setFrozen(False, affectObjects=affectObjects)


# register the symbol
cross3d.registerSymbol('SceneLayerGroup', AbstractSceneLayerGroup, ifNotFound=True)
