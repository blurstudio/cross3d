##
#	\namespace	cross3d.studiomax.studiomaxscene
#
#	\remarks	The StudiomaxScene class will define all the operations for Studiomax scene interaction.
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax 											import mxs
from cross3d.abstract.abstractscenelayergroup 		import AbstractSceneLayerGroup

class StudiomaxSceneLayerGroup( AbstractSceneLayerGroup ):
	def _nativeObjects( self ):
		"""
			\remarks	implements the AbstractSceneLayerGroup._nativeObjects method to pull the native objects from the layers in this group
			\return		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
		"""
		output = []
		for layer in self.layers():
			output += layer._nativeObjects()
		return output

	def displayName( self ):
		"""
			\remarks	implements the AbstractSceneLayerGroup.name method to retrieve the unique layer display name for this layer
			\return		<str> name
		"""
		return self._nativePointer

	def name( self ):
		"""
			\remarks	implements the AbstractSceneLayerGroup.name method to retrieve the unique layer name for this layer
			\return		<str> name
		"""
		return self._nativePointer

	def groupOrder( self ):
		"""
			\remarks	returns the index that this layer group is currently in
			\return		<int>
		"""
		name 	= str(self.name())
		gn 		= list(self._scene.metaData().value( 'layerGroupNames' ))
		if ( name in gn ):
			return gn.index( name )
		return -1

	def isOpen( self ):
		"""
			\remarks	implements the AbstractLayerGroup.setOpen method to return whether or not the layer group is open
			\return		<bool> open
		"""
		data 	= self._scene.metaData()
		names 	= list(data.value('layerGroupNames'))
		states 	= list(data.value('layerGroupStates'))

		name 	= str(self.name())
		if ( name in names ):
			return states[names.index(name)]
		return False

	def layers( self ):
		"""
			\remarks	implements the AbstractLayerGroup.layers method to retrieve the layers that are currently on this group
			\return		<list> [ <cross3d.SceneLayer>, .. ]
		"""
		gi		= self.groupOrder()
		output 	= []
		for layer in self._scene.layers():
			if ( layer.name() == 'World Layer' ):
				continue

			data 	= layer.metaData()
			lgi 	= data.value( 'groupIndex' ) - 1
			if ( lgi == gi ):
				output.append( layer )

		output.sort( lambda x,y: cmp( x.metaData().value( 'groupOrder' ), y.metaData().value( 'groupOrder' ) ) )
		return output

	def remove( self, removeLayers = False, removeObjects = False ):
		"""
			\remarks	implements the AbstractLayerGroup.remove method to remove the layer from the scene (layers included when desired)
			\param		removeLayers	<bool>	when true, the layers in the layer group should be removed from the scene, otherwise
												only the layer group should be removed
			\param		removeObjects	<bool>	if removeLayers is true, when removeObjects is true, the objects on the layers in the
												layer group should be removed from the scene
			\return		<bool> success
		"""
		data 	= self._scene.metaData()
		names 	= list(data.value( 'layerGroupNames' ))
		states	= list(data.value( 'layerGroupStates' ))

		# requires at least 1 group
		if ( len(names) == 1 ):
			return False

		layers = self.layers()

		# remove the layers from the scene
		if ( removeLayers ):
			for layer in layers:
				layer.remove( removeObjects = removeObjects )

		# update the layers to be in the root group
		else:
			for layer in layers:
				ldata = layer.metaData()
				ldata.setValue( 'groupIndex', 1 )

		# remove this group from the scene
		index = names.index( self.name() )
		names 	= names[:index] + names[index+1:]
		states 	= states[:index] + states[index+1:]

		data.setValue( 'layerGroupNames', names )
		data.setValue( 'layerGroupStates', states )

		# update all the layers past this index
		for layer in self._scene.layers():
			ldata 	= layer.metaData()
			gi 		= ldata.value('groupIndex') - 1
			if ( index < gi ):
				ldata.setValue( 'groupIndex', gi )

		return True

	def setDisplayName( self, name ):
		"""
			\remarks	implements the AbstractLayerGroup.setName method to set the display name for this layer group
			\param		name	<str>
			\return		<bool> changed
		"""
		# make sure we are changing
		if ( name == self.name() ):
			return False

		name	 	= str(name)
		data		= self._scene.metaData()
		names 		= list(data.value( 'layerGroupNames' ))

		# make sure we have a unique name
		if ( name in names ):
			return False

		index 				= names.index(self.name())
		names[index] 		= name
		self._nativePointer = name
		data.setValue( 'layerGroupNames', names )
		return True

	def setGroupOrder( self, groupOrder ):
		"""
			\remarks	implements the AbstractLayerGroup.setGroupOrder method to set the order number for this layer group
			\param		groupOrder	<int>
			\return		<bool> changed
		"""
		# make sure we are chaning
		if ( groupOrder == self.groupOrder() ):
			return False

		groupName 	= str(self.name())
		data		= self._scene.metaData()
		orignames	= list(data.value('layerGroupNames'))
		states		= list(data.value('layerGroupStates'))

		if ( not groupName in orignames ):
			return False

		index 	= orignames.index(groupName)
		state 	= states[index]
		names 	= orignames[:index] + orignames[index+1:]
		states 	= states[:index] + states[index+1:]

		names.insert( groupOrder, groupName )
		states.insert( groupOrder, state )

		data.setValue( 'layerGroupNames', names )
		data.setValue( 'layerGroupStates', states )

		# update the layers
		for layer in self._scene.layers():
			ldata = layer.metaData()
			gi = ldata.value('groupIndex')
			try:
				oname = orignames[gi-1]
			except IndexError:
				return False
			ldata.setValue( 'groupIndex', names.index(oname) + 1 )

		return True

	def setOpen( self, state ):
		"""
			\remarks	implements the AbstractLayerGroup.setOpen method to set whether or not the layer group is open
			\return		<bool> open
		"""
		data	= self._scene.metaData()
		names 	= list(data.value('layerGroupNames'))
		states 	= list(data.value('layerGroupStates'))

		name 	= str(self.name())
		if ( name in names ):
			states[names.index(name)] = state
			data.setValue( 'layerGroupStates', states )
			return True
		return False

	def sortLayers(self, key=lambda x: x.name()):
		layers = self.layers()
		layers.sort(key=key)
		for index, layer in enumerate(layers):
			print layer.name(), index
			layer.setLayerGroupOrder(index)
		# self.parent().refresh()

# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneLayerGroup', StudiomaxSceneLayerGroup )
