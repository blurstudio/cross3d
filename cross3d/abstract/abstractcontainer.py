##
#	\namespace	blur3d.api.abstract.abstractcontainer
#
#	\remarks	The AbstractContainer class provides an interface for objects that "group" several scene objects.
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d import abstractmethod
from blur3d.constants import ObjectType
from blur3d.api import SceneWrapper
from blur3d import api

class AbstractContainer(SceneWrapper):
	"""
		The SceneObjectGroup class provides an interface for working on sets of 
		SceneObject's as a singular group
	"""

	def __init__(self, scene, nativeGroup):
		SceneWrapper.__init__(self, scene, nativeGroup)

		# define custom properties
		self._materialOverride				 = None			# blur3d.api.SceneMaterial 					- material to be used as the override material for the objects in this group
		self._materialOverrideFlags			 = 0				# blur3d.constants.MaterialOverrideOptions		- options to be used when overriding materials
		self._materialOverrideAdvancedState = {}			# <dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		self._propSetOverride				 = None			# blur3d.api.SceneObjectPropSet				- property set to be used as the override properties for the objects in this group

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _addNativeAtmospherics(self, nativeAtmospherics):
		"""Add the native atmospherics to the object group
		
		:param nativeAtmospherics: list of nativeAtmospherics
		:return: bool
		
		"""
		return False

	@abstractmethod
	def _addNativeFx(self, nativeFx):
		"""Add the native fx to the object group

		:param nativeFx: list of nativeFx items
		:return bool

		"""
		return False

	@abstractmethod
	def _addNativeObjects(self, nativeObjects):
		"""
			\remarks	add the native objects to the object group
			\sa			addObjects, addSelection
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		return False

	def _clearNativeMaterialOverride(self):
		"""
			\remarks	[virtual] clear the native objects of any material overrides for this group
			\sa			blur3d.api.Scene._clearNativeMaterialOverride
			\return		<bool> success
		"""
		return self._scene._clearNativeMaterialOverride(self._nativeObjects())

	def _clearNativePropSetOverride(self):
		"""
			\remarks	[virtual] clear the native objects of any property set overrides for this group
			\sa			blur3d.api.Scene._clearNativePropSetOverride
			\return		<bool> success
		"""
		return self._scene._clearNativePropSetOverride(self._nativeObjects())

	@abstractmethod
	def _nativeAtmospherics(self):
		"""
			\remarks	return a list of the atmospherics that are associated with this object group
			\sa			atmospherics
			\return		<list> [ <variant> nativeAtmospheric, .. ]
		"""
		return []

	@abstractmethod
	def _nativeFxs(self):
		"""
			\remarks	return a list of the fx that are associated with this object group
			\sa			fxs
			\return		<list> [ <variant> nativeFx, .. ]
		"""
		return []

	@abstractmethod
	def _nativeObjects(self):
		"""
			\remarks	return a list of the native objects that are currently on this group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return []

	@abstractmethod
	def _nativeMaterials(self):
		"""
			\remarks	return a list of all the native materials that are contained within this object group
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		return []

	@abstractmethod
	def _nativeMaterialOverride(self):
		"""
			\remarks	return the current override material for this object group
			\return		<variant> nativeMaterial || None
		"""
		return None

	@abstractmethod
	def _setNativeAtmospherics(self, nativeAtmospherics):
		"""
			\remarks	set the linked atmopherics to this object group to the inputed list of atmospherics
			\param		nativeAtmospherics	<list> [ <variant> nativeAtmospheric, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeFxs(self, nativeFxs):
		"""
			\remarks	set the linked fxs to this object group to the inputed list of fxs
			\param		nativeFxs	<list> [ <variant> nativeFx, .. ]
			\return		<bool> success
		"""
		return False

	def _setNativeMaterialOverride(self, nativeMaterial, options= -1, advancedState=None):
		"""
			\remarks	[virtual] set the current override materials for this object group
			\sa			blur3d.api.Scene._setNativeMaterialOverride
			\param		nativeMaterial 	<variant> || None
			\param		options			<blur3d.constants.MaterialOverrideOptions>
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
			\return		<bool> success
		"""
		if (options == -1):
			options = self.materialOverrideFlags()
		else:
			self.setMaterialOverrideFlags(options)

		if (advancedState == None):
			advancedState = self.materialOverrideAdvancedState()
		else:
			self.setMaterialOverrideAdvancedState(advancedState)

		return self._scene._setNativeMaterialOverride(self._nativeObjects(), nativeMaterial, options=options, advancedState=advancedState)

	def _setNativePropSetOverride(self, nativePropSet):
		"""
			\remarks	[virtual] set the current override property set for this object group
			\sa			blur3d.api.Scene._setNativePropSetOverride
			\param		nativePropSet 	<variant> || None
			\return		<bool> success
		"""
		if (nativePropSet):
			return self._scene._setNativePropSetOverride(self._nativeObjects(), nativePropSet)
		else:
			return self._scene._clearNativePropSetOverride(self._nativeObjects())

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def addAtmospherics(self, atmospherics):
		"""Add the atmospherics to this object group
		
		:param atmospherics: list of :class:`blur3d.api.SceneAtmospheric` 
		                     objects
		:return: bool
		
		"""
		return self._addNativeAtmospherics([ atmos.nativePointer() for atmos in atmospherics ])

	def addFxs(self, fxs):
		"""Add the fxs to this object group
		
		:param fxs: list of :class:`blur3d.api.SceneFx` 
		                     objects
		:return: bool
		
		"""
		return self._addNativeFxs([ fx.nativePointer() for fx in fxs ])

	def addObjects(self, objects):
		"""Add the objects to this object group
		
		:param objects: list of :class:`blur3d.api.SceneObject` objects
		:return: bool
		
		"""
		return self._addNativeObjects([ object.nativePointer() for object in objects ])

	def addSelection(self):
		"""
		Add the selected scene objects to this object group
		
		:return: bool
		
		"""
		return self._addNativeObjects(self._scene._nativeSelection())

	def atmospherics(self):
		"""Return a list of the atmospherics that are part of this object group
			
		:return: list of :class:`blur3d.api.SceneAtmospheric` objects
		
		"""
		from blur3d.api import SceneAtmospheric
		return [ SceneAtmospheric(self._scene, atmos) for atmos in self._nativeAtmospherics() ]

	def clearMaterialOverride(self):
		"""
		Clears the current material overrides from this object group's objects
		
		:return: bool
		
		"""
		return self._clearNativeMaterialOverride()

	def clearMaterialOverrideFlags(self):
		"""
		Return whether or not the inputed flag is set in the override options
		
		:return: bool
		
		"""
		self._materialOverrideFlags = 0
		return True

	def clearPropSetOverride(self):
		"""
		Clears the current prop set override from this object group's objects
		
		:return: bool
		
		"""
		return self._clearNativePropSetOverride()

	def deselect(self):
		"""Deselects the objects on this object group from the scene
		
		:return: bool
		
		"""
		return self.setSelected(False)

	def freeze(self):
		"""
		Freezes (locks) the objects on this object group in the scene
		
		:return: bool
		
		"""
		return self.setFrozen(True)

	def fxs(self):
		"""Return a list of the fxs that are part of this object group
			
		:return: list of :class:`blur3d.api.SceneFx` objects
		
		"""
		from blur3d.api import SceneFx
		return [ SceneFx(self._scene, fx) for fx in self._nativeFxs() ]

	def hasMaterialOverrideFlag(self, flag):
		"""
		Return whether or not the inputed flag is set in the override options
		
		:param flag: :data:`blur3d.constants.MaterialOverrideOptions`
		:return: bool

		"""
		return (self._materialOverrideFlags & flag) != 0

	def hide(self):
		"""
		Hides the objects on this object group in the scene
		
		:return: bool
		
		"""
		return self.setHidden(True)

	def isEmpty(self):
		"""
		Returns whether or not this object group is empty (contains no chidren)
		
		:return: bool
		
		"""
		return len(self._nativeObjects()) == 0

	@abstractmethod
	def isFrozen(self):
		"""
		Retrieve the group name for this object group instance
		
		:return: bool
		
		"""
		return False

	@abstractmethod
	def isHidden(self):
		"""
		Retrieve the group name for this object group instance
		
		:return: bool
		
		"""
		return False

	def isVisible(self):
		"""
		Return whether or not this object group is visible
		
		:return: bool
		
		"""
		return not self.isHidden()

	def isolate(self):
		"""
		Isolates the objects in this group in the scene
		
		:return: bool
		
		"""
		return self._scene._isolateNativeObjects(self._nativeObjects())

	def nativePointer(self):
		"""
		Return the pointer to the native object that is wrapped
		
		:return: native object
		
		"""
		return self._nativePointer

	def objects(self):
		"""
		Returns the SceneObject's that are associated with this object group
		
		:return: a list of :class:`blur3d.api.SceneObject` objects
		
		"""
		from blur3d.api import SceneObject
		return [ SceneObject(self._scene, obj) for obj in self._nativeObjects() ]

	def materials(self):
		"""
		Return a list of all the materials contained within this object group
		
		:return: a list of :class:`blur3d.api.SceneMaterial` objects
		
		"""
		from blur3d.api import SceneMaterial
		return [ SceneMaterial(self._scene, mtl) for mtl in self._nativeMaterials() ]

	def materialOverride(self):
		"""
		Return the current override material for this object set
		
		:return: :class:`blur3d.api.SceneMaterial` or None
		
		"""
		nativeMaterial = self._nativeMaterialOverride()
		if (nativeMaterial):
			from blur3d.api import SceneMaterial
			return SceneMaterial(self.scene(), nativeMaterial)
		return None

	def materialOverrideAdvancedState(self):
		"""
		Return the current advanced material override state that the object 
		group is in
		
		:return: <dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		"""
		return self._materialOverrideAdvancedState

	def materialOverrideFlags(self):
		"""
		Return the duplication flags for the override material
		
		:return: :data:`blur3d.constants.MaterialOverrideOptions`

		"""
		return self._materialOverrideFlags

	def propSetOverride(self):
		"""
		Return the current override prop set for this object set
		
		:return: :class:`blur3d.api.SceneObjectPropSet` or None
		
		"""
		from blur3d.api import ScenePropSet
		nativePropSet = self._nativePropSetOverride()
		if (nativePropSet and not isinstance(nativePropSet, ScenePropSet)):
			return ScenePropSet(self.scene(), nativePropSet)
		return nativePropSet

	@abstractmethod
	def remove(self, removeObjects=False):
		"""
		Remove the object group from the scene (objects included when desired)
		
		:param removeObjects: When true, the objects on the object group 
							  should be removed from the scene, otherwise
							  only the object group should be removed
		:return: bool
			
		"""
		return False

	def select(self):
		"""Selects the items on this object group
		
		:return: bool
			
		"""
		return self.setSelected(True)

	@abstractmethod
	def setActive(self, state):
		"""
		Mark this object group as the active scene object group
		
		:return: bool
		
		"""
		return False

	def setMaterialOverride(self, material, options= -1, advancedState=None):
		"""
		Set the override material on the objects for this set
		
		:param material: :class:`blur3d.api.SceneMaterial` or None
		:param options: :data:`blur3d.constants.MaterialOverrideOptions`
		:param advancedState: <dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		
		:return: bool
		
		"""
		nativeMaterial = None
		if (material):
			nativeMaterial = material.nativePointer()

		if (options == -1):
			options = self.materialOverrideFlags()

		return self._setNativeMaterialOverride(nativeMaterial, options=options, advancedState=advancedState)

	def setMaterialOverrideFlag(self, flag, state=True):
		"""
		Set the inputed flag on or off based on the state
		
		:param flag: :data:`blur3d.constants.MaterialOverrideOptions`
		:param state: bool
		:return: bool

		"""
		if (state):
			self._materialOverrideFlags |= flag
		else:
			self._materialOverrideFlags ^= flag
		return True

	def setMaterialOverrideFlags(self, flags):
		"""
		Set all of the duplication flags for override materials
		
		:param flags: :data:`blur3d.constants.MaterialOverrideOptions`
		:return: bool
		
		"""
		self._materialOverrideFlags = flags
		return True

	def setMaterialOverrideAdvancedState(self, advancedState):
		"""
		Set an advanced state for this object group to be in
		
		:param advanceState: <dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		:return: bool
		
		"""
		self._materialOverrideAdvancedState = advancedState

	def setAtmospherics(self, atmospherics):
		"""
		Sets the atmospherics that are associated with this object group 
		to the inputed list of atmospherics
		
		:param atmospherics: list of :class:`blur3d.api.SceneAtmospheric`
		                     objects
		:return: bool

		"""
		return self._setNativeAtmospherics([ atmos.nativePointer() for atmos in atmospherics ])

	def setFxs(self, fxs):
		"""
		Sets the fxs that are associated with this object group 
		to the inputed list of fxs
		
		:param fxs: list of :class:`blur3d.api.SceneFx`
		                     objects
		:return: bool

		"""
		return self._setNativeFxs([ fx.nativePointer() for fx in fxs ])

	def setPropSetOverride(self, propSet):
		"""
		Set the override properties on the objects that are a part of 
		this object group
		
		:param propSet: :class:`blur3d.api.SceneObjectPropSet`
		:return: bool
		
		"""
		nativePropSet = None
		if (propSet):
			nativePropSet = propSet.nativePointer()

		return self._setNativePropSetOverride(nativePropSet)

	def setFrozen(self, state):
		"""
		Set the frozen (locked) state for the objects on this object group
		
		:param state: bool
		:return: bool

		"""
		return self._scene._freezeNativeObjects(self._nativeObjects(), state)

	def setHidden(self, state, options=None):
		"""
		Set the hidden state for the objects on this object group

		:param state: bool
		:param options: :data:`blur3d.constants.VisibilityToggleOptions`
		:return: bool
		
		"""
		objs = self._nativeObjects()
		self._scene._hideNativeObjects(objs, state)
		return True

	def setSelected(self, state):
		"""
		Sets the selected state of the objects on this object group
		
		:param state: bool
		:return: bool

		"""
		return self._scene._setNativeSelection(self._nativeObjects())

	def setVisible(self, state):
		"""
		Set whether or not this object group is visible
		
		:param state: bool
		:return: bool

		"""
		return self.setHidden(not state)

	def unhide(self):
		"""Unhides the objects on this object group
		
		:return: bool

		"""
		return self.setHidden(False)

	def unfreeze(self):
		"""Unfreezes the objects on this object group
		
		:return: bool

		"""
		return self.setFrozen(False)


# register the symbol
api.registerSymbol('Container', AbstractContainer, ifNotFound=True)
