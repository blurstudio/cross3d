##
#	\namespace	cross3d.abstract.abstractscenelayer
#
#	\remarks	The AbstractSceneLayer provides a cross-application interface to 3d scene layer's and their interaction
#				This class will provide the base implementation and definition of methods that will need to be re-implemented
#				to hanel per-application usage
#
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import abstractmethod
from abstractcontainer import AbstractContainer

class AbstractSceneLayer(AbstractContainer):

	def __init__(self, scene, nativeLayer):
		AbstractContainer.__init__(self, scene, nativeLayer)

		# define custom properties
		self._altMtlIndex		 = -1
		self._altPropIndex		 = -1

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	@abstractmethod
	def _nativeAltMaterials(self):
		"""
			\remarks	return a list of the alternate materials associated with this layer

			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		return []

	@abstractmethod
	def _nativeLayerGroup(self):
		"""
			\remarks	return the layer group that this layer belongs to

			\return		<variant> nativeLayerGroup || None
		"""
		return None

	@abstractmethod
	def _setNativeAltMaterialAt(self, index, nativeMaterial):
		"""
			\remarks	set the material in the alternate materials list at the inputed index to the given material
			\param		index			<index>
			\param		nativeMaterial	<variant> || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeAltMaterials(self, nativeMaterials):
		"""
			\remarks	set the alternate material list for this layer
			\param		nativeMaterials	<list> [ <variant> nativeMaterial, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeLayerGroup(self, nativeLayerGroup):
		"""
			\remarks	set the layer group that this layer belongs to

			\param		<variant> nativeLayerGroup || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeWireColor(self, nativeColor):
		"""
			\remarks	set the wirecolor for this layer instance

			\param		nativeColor		<variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _nativeWireColor(self):
		"""
			\remarks	return the wirecolor for this layer instance

			\return		<variant> nativeColor || None
		"""
		return None

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def addAltMaterial(self, material):
		"""
		Add the inputed material to the list of possible alternate
		materials for this layer

		:param material: :class:`cross3d.SceneMaterial`

		"""
		altMtls = self.altMaterials()
		altMtls.append(material)
		return self.setAltMaterials(altMtls)

	def addAltPropSet(self, propSet):
		"""
		Add the property set to the list of possible alternate property
		sets for this layer

		:param propSet: :class:`cross3d.ScenePropSet`

		"""
		propSets = self.altPropSets()
		propSets.append(propSet)
		return self.setAltPropSets(propSets)

	@abstractmethod
	def advancedAltMaterialStateAt(self, index):
		"""
		Return a mapping for the advanced alternate material status of a
		given alternate material slot

		:param index: int
		:return: A dictionary with the BaseMaterialID as keys with values of
		         tuples of (SceneMaterial, ignored)

		         {int baseMaterialId: (:class:`cross3d.SceneMaterial` override, bool ignored), .. }

		"""
		return {}

	def altMaterialAt(self, index):
		"""Retrieve the alternate material at the inputed index

		:param index: int
		:return: :class:`cross3d.SceneMaterial` or None

		"""
		mtls = self._nativeAltMaterials()
		if (0 <= index and index < len(mtls)):
			mtl = mtls[index]
			if (mtl):
				from cross3d import SceneMaterial
				return SceneMaterial(self._scene, mtl)
			else:
				return None
		return None

	def altMaterialCount(self):
		"""
			\remarks	return the number of alternate materials that this layer is associated with

			\return		<int> count
		"""
		return len(self._nativeAltMaterials())

	def altMaterials(self):
		"""
			\remarks	return a list of the alternate materials held by this layer

			\return		<list> [ <cross3d.SceneMaterial>, .. ]
		"""
		from cross3d import SceneMaterial
		output = []
		for mtl in self._nativeAltMaterials():
			if (mtl):
				output.append(SceneMaterial(self._scene, mtl))
			else:
				output.append(None)
		return output

	@abstractmethod
	def altMaterialFlags(self):
		"""Return a list of material duplication flags for this layer

		:return: a list of :data:`cross3d.constants.MaterialDuplicateOptions`'s

		"""
		return []

	def altMaterialFlagsAt(self, index):
		"""Return the material flags at the inputed index

		:return: :data:`cross3d.constants.MaterialDuplicateOptions`

		"""
		flags = self.altMaterialFlags()
		if (0 <= index and index < len(flags)):
			return flags[index]
		return 0

	def altPropSetAt(self, index):
		"""Retrive the alternate SceneObjectPropSet at the inputed index

		:return: :class:`cross3d.SceneObjectPropSet` or None

		"""
		propsets = self.altPropSets()
		if (0 <= index and index < len(propsets)):
			return propsets[index]
		return None

	def altPropSetCount(self):
		"""Retrieve the number of alternate SceneObjectPropSet's for this layer

		"""
		return len(self.altPropSets())

	@abstractmethod
	def altPropSets(self):
		"""Retrive the alternate SceneObjectPropSet's for this layer

		:return: a list of :class:`cross3d.SceneObjectPropSet`'s

		"""
		return []

	def defineAltMaterialAt(self, index, material):
		"""
		Defines a new material for the inputed index, provided the
		material at that index is not already defined

		:param index: int
		:param material: :class:`cross3d.SceneMaterial`
		:rtype: bool

		"""
		existing = self.altMaterialAt(index)
		if (not existing):
			return self.setAltMaterialAt(index, material)
		return False

	def defineAltPropSetAt(self, index, propSet):
		"""
		Defines a new property set for the inputed index, provided the
		property set at that index is not already defined

		:param index: int
		:param propSet: :class:`cross3d.ScenePropSet`
		:rtype: bool

		"""
		existing = self.altPropSetAt(index)
		if (not (existing and existing.isActive())):
			return self.setAltPropSetAt(index, propSet)
		return False

	def currentAltMaterialIndex(self):
		"""Retrieve the index of the currently applied alternate material
		for this layer

		:rtype: int

		"""
		return self._altMtlIndex

	def currentAltMaterial(self):
		"""Retrieve the current alt material

		:rtype: :class:`cross3d.SceneMaterial`

		"""
		return self.altMaterialAt(self._altMtlIndex)

	def currentAltPropSetIndex(self):
		"""Retrieve the alternate object property set index

		:rtype: int

		"""
		return self._altPropIndex

	def currentAltPropSet(self):
		"""Retrieve the alternate object property set at the inputed index

		:rtype: :class:`cross3d.ScenePropSet`

		"""
		return self.altPropSetAt(self._altPropIndex)

	def hasAltMaterialFlagAt(self, index, flag):
		"""
		Return whether or not a given material duplication flag is set for
		the inputed alt material index

		:param index: int
		:param flag: :data:`cross3d.constants.MaterialDuplicateOptions`
		:return: found
		:rtype: bool

		"""
		flags = self.altMaterialFlags()
		if (0 <= index and index < len(flags)):
			return (flags[index] & flag) != 0
		return False

	@abstractmethod
	def hasAdvancedAltMaterialStateAt(self, index):
		"""
		Return whether or not an advanced state for an alternate material
		has been defined for the inputed

		"""
		return False

	def indexOfAltMaterial(self, material):
		"""Return the index of the inputed material for the current layer

		:param: :class:`cross3d.SceneMaterial`
		:return: index of material, or -1 if not found

		"""
		mtls = self.altMaterials()
		try:
			return mtls.index(material)
		except:
			return -1

	def indexOfAltPropSet(self, propSet):
		"""Return the index of the inputed property set for the current layer

		:param propSet: :class:`cross3d.ScenePropSet`
		:return: index of material, or -1 if not found

		"""
		propSets = self.altPropSets()
		try:
			return propSets.index(propSet)
		except:
			return -1

	@abstractmethod
	def isActive(self):
		"""Return whether or not this layer is currently active in the scene

		"""
		return False

	@abstractmethod
	def isWorldLayer(self):
		"""Return whether or not this layer is the root world layer of the
		scene

		"""
		return False

	def isolate(self):
		"""
		Reimplements the :meth:`cross3d.SceneObjectGroup.isolate` method
		to isolate just this layer (hide all other layers)

		"""
		scene = self._scene

		for layer in scene.layers():
			if (not layer == self):
				layer.hide()
			else:
				layer.unhide()

		scene.emitLayerStateChanged()
		return True

	def groupName(self):
		"""
		Implements the :meth:`cross3d.SceneObjectGroup.groupName`
		method to retrieve the group name for this object group instance

		"""
		layerGroup = self.layerGroup()
		if (layerGroup):
			return layerGroup.groupName()
		return ''

	def layerGroup(self):
		"""Return the layer group that this layer belongs to

		:return: :class:`cross3d.SceneLayerGroup` or None

		"""
		nativeGroup = self._nativeLayerGroup()
		if (nativeGroup):
			from cross3d import SceneLayerGroup
			return SceneLayerGroup(self._scene, nativeGroup)
		return None

	@abstractmethod
	def layerGroupOrder(self):
		"""Return the sort order for this layer within its layer group

		"""
		return -1

	def recordLayerState(self, xml):
		"""Records the layer's current state to xml

		:param xml: :class:`cross3d.migrate.XMLElement`

		"""
		# don't bother recording hidden layers
		if self.isHidden():
			return False

		# record the layer state
		node = xml.addNode('layer')
		node.setAttribute('name', 		self.name())
		node.setAttribute('id', 		self.uniqueId())

		# record the propSetOverride
		propSet = self.propSetOverride()
		if (propSet):
			propSet.recordXml(node.addNode('propSetOverride'))

		# record the material override
		material = self.materialOverride()
		if (material):
			material.recordXml(node.addNode('materialOverride'))

		# record the environment override for the world layer
		if (self.isWorldLayer()):
			override = self._scene.environmentMapOverride()
			if (override):
				override.recordXml(node.addNode('environmentMapOverride'))

		return True

	def restoreLayerState(self, xml):
		"""Restore the layer's state from the inputed xml

		:param xml: :class:`cross3d.migrate.XML.XMLDocument`

		"""
		if (not xml):
			return False

		# set visible
		self.setHidden(False, affectObjects=True)

		# determine the alterante state for this layer
		scene = self._scene
		from cross3d import SceneMaterial, SceneMap, SceneObjectPropSet
		self.setPropSetOverride(SceneObjectPropSet.fromXml(scene, xml.findChild('propSetOverride')))
		self.setMaterialOverride(SceneMaterial.fromXml(scene, xml.findChild('materialOverride')))

		# restore environment override
		if (self.isWorldLayer()):
			scene.setEnvironmentMapOverride(SceneMap.fromXml(scene, xml.findChild('environmentMapOverride')))

	def removeAltMaterialAt(self, index):
		"""Remove the material at the inputed index from the material list

		"""
		altMtls = self.altMaterials()
		if (0 <= index and index < len(altMtls)):
			# reset the alternate materials for this layer
			self.setAltMaterials(altMtls[:index] + altMtls[index + 1:])

			# remove any advanced alternate material states at the given index
			self.removeAdvancedAltMaterialStateAt(index)
			return True
		return False

	@abstractmethod
	def removeAdvancedAltMaterialStateAt(self, index):
		"""
		Remove the advanced alternate material state from the layer at
		the alternate material index

		"""
		return False

	def removeAltPropSetAt(self, index):
		"""
		Remove the propset at the inputed index from this layer's list of
		alternate property sets

		"""
		altPropSets = self.altPropSets()
		if (0 <= index and index < len(altPropSets)):
			return self.setAltPropSets(altPropSets[:index] + altPropSets[index + 1:])
		return False

	@abstractmethod
	def setActive(self, state):
		"""Mark this layer as the active scene layer

		"""
		return False

	def setAltMaterialAt(self, index, material):
		"""
		Sets the alternate material at the inputed index to the given
		material instance

		"""
		nativePointer = None
		if (material):
			nativePointer = material.nativePointer()

		return self._setNativeAltMaterialAt(index, nativePointer)

	def setAltMaterials(self, materials):
		"""Sets the alternate material list for this layer

		"""
		mtls = []
		for mtl in materials:
			if (mtl):
				mtls.append(mtl.nativePointer())
			else:
				mtls.append(None)

		return self._setNativeAltMaterials(mtls)

	def setAltMaterialFlagAt(self, index, flag, state=True):
		"""
		Set whether or not a given material duplication flag is on for the
		inputed alt material index

		:param index: int
		:param flat: :data:`cross3d.constants.MaterialDuplicateOptions`
		:param state: bool

		"""
		flags = self.altMaterialFlags()
		if (0 <= index and index < len(flags)):
			if (state):
				flags[index] |= flag
			else:
				flags[index] ^= flag

			return self.setAltMaterialFlags(flags)
		return False

	def setAltMaterialFlagsAt(self, index, flags):
		"""
		Set the alternate material flags at the inputed index for this instance

		:param index: int
		:param flags: :data:`cross3d.constants.MaterialDuplicateOptions`

		"""
		mflags = self.altMaterialFlags()
		if (0 <= index and index < len(mflags)):
			mflags[index] = flags
			return self.setAltMaterialFlags(mflags)
		return False

	@abstractmethod
	def setAltMaterialFlags(self, flags):
		"""Set the alternate material flags for this instance

		:param flags: list of
		              :data:`<cross3d.constants.MaterialDuplicateOptions`'s

		"""
		return False

	@abstractmethod
	def setAltPropSetAt(self, index, propSet):
		"""Set the alternate object property set at the inputed index

		"""
		return False

	@abstractmethod
	def setAltPropSets(self, propSets):
		"""Set the alternate object property set list for this layer

		"""
		return False

	def setCurrentAltMaterialIndex(self, index):
		"""
		Set the current index for the alternate material, applying the
		alternate material when necessary

		"""
		# do not need to reprocess
		if (index == self._altMtlIndex):
			return False

		mtls = self.altMaterials()

		# apply an override state
		if (0 <= index and index < len(mtls)):
			self._altMtlIndex = index
			return self.setMaterialOverride(mtls[index])

		# clear an override state
		elif (index == -1):
			self._altMtlIndex = index
			return self.clearMaterialOverride()

		return False

	def setCurrentAltPropSetIndex(self, index):
		"""
		Set the current index for the alternate object property set,
		applyting the set to the objects on this layer when necessary

		"""
		# do not need to reprocess
		if (index == self._altPropIndex):
			return False

		propsets = self.altPropSets()

		# apply an override state
		if (0 <= index and index < len(propsets) and propsets[index].isActive()):
			if (self.setPropSetOverride(propsets[index])):
				self._altPropIndex = index
				return True
			return False

		# clear the override state
		elif (index == -1):
			if (self.clearPropSetOverride()):
				self._altPropIndex = index
				return True
			return False

		else:
			return False

	def setGroupName(self, name):
		"""
		Implements the AbstractContainer.groupName method to set the
		group name for this object group instance

		"""
		layerGroup = self._scene.findLayerGroup(name)
		if (layerGroup):
			return self.setLayerGroup(layerGroup)
		return False

	def setMaterialOverride(self, material, options= -1, advancedState=None):
		"""
		Overloads the :meth:`cross3d.SceneObjectGroup.setMaterialOverride`
		method to make sure we get recorded alternate properties before
		applying overrides

		:param material: :class:`cross3d.SceneMaterial`
		:param options: :data:`cross3d.constants.MaterialOverrideOptions`
		:param advancedState: <dict> { <int> baseMaterialId: ( <cross3d.gui.SceneMaterial> override, <bool> ignored ) }

		"""
		amtls = self.altMaterials()

		# make sure we have the advanced material state options
		if (material in amtls):
			index			 = amtls.index(material)
			options 		 = self.altMaterialFlagsAt(index)
			advancedState	 = self.advancedAltMaterialStateAt(index)

		return AbstractContainer.setMaterialOverride(self, material, options=options, advancedState=advancedState)

	def setLayerGroup(self, layerGroup):
		"""Set the layer group that this layer is associated with

		:param layerGroup: :class:`cross3d.SceneLayerGroup` or None

		"""
		nativeGroup = None
		if (layerGroup):
			nativeGroup = layerGroup.nativePointer()

		return self._setNativeLayerGroup(nativeGroup)

	@abstractmethod
	def setLayerGroupOrder(self, groupOrder):
		"""Set the layer group sort order for this layer within its layer group

		"""
		return False

	@abstractmethod
	def setAdvancedAltMaterialStateAt(self, index, altMaterialState):
		"""
		Set a mapping for the advanced alternate material status of a given
		alternate material slot

		:param index: int
		:param altMaterialState: <dict> [ <int> baseMaterialId: (<cross3d.SceneMaterial> override, <bool> ignored), .. }

		"""
		return False

	def setWireColor(self, color):
		"""Set the wire color for this layer

		:param color: :class:`PyQt4.QtGui.QColor`

		"""
		return self._setNativeWireColor(self._scene._toNativeValue(color))

	def wireColor(self):
		"""Return the wire color for this layer

		:rtype: :class:`PyQt4.QtGui.QColor`

		"""
		clr = self._nativeWireColor()
		if (clr):
			return self._scene._fromNativeValue(clr)

		from PyQt4.QtGui import QColor
		return QColor()

	@staticmethod
	def fromXml(scene, xml):
		"""Create a new layer from the inputed xml data

		:param xml: :class:`cross3d.migrate.XMLElement`

		"""
		if (xml):
			return scene.findLayer(name=xml.attribute('name'), uniqueId=int(xml.attribute('id', 0)))
		return None


# register the symbol
cross3d.registerSymbol('SceneLayer', AbstractSceneLayer, ifNotFound=True)
