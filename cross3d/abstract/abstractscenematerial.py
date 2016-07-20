##
#	\namespace	cross3d.abstract.abstractscenematerial
#
#	\remarks	The AbstractSceneMaterial class provides an interface for editing
#				materials in a Scene environment within any DCC application.
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import SceneWrapper, abstractmethod

# =============================================================================
# CLASSES
# =============================================================================

class AbstractSceneMaterial(SceneWrapper):
	"""An abstract interface for SceneMaterials.

	The AbstractSceneMaterial class provides an interface for editing
	materials in a Scene environment within any DCC application.
	"""
	@abstractmethod
	def _nativeObjects(self):
		"""The native objects using this material."""
		return []

	@abstractmethod
	def _nativeSubmaterials(self):
		"""The native sub-materials for this material instance."""
		return []

	@abstractmethod
	def edit(self):
		"""Allow the user to edit the material."""
		return False

	@classmethod
	def editMaterials(self, materials=[]):
		""" Clear any existing and display the provided materials.
		
		Args:
			materials (list): A list of materials. Defaults to a empty list.
		
		Returns:
			bool: Success.
		"""
		return False

	def materialType(self):
		"""The material type for this material instance
		
		Returns:
			`cross3d.constants.MaterialType`
		"""
		from cross3d.constants import MaterialType
		return MaterialType.Generic

	def objects(self):
		"""The objects that are using this material.

		Returns:
			list: The list of `cross3d.SceneObject`s using this material.
		"""
		from cross3d import SceneObject
		return [SceneObject(self._scene, o) for o in self._nativeObjects() if o]

	def submaterials(self):
		"""The sub-materials for this material.

		Returns:
			list: `cross3d.SceneMaterial`
		"""
		from cross3d import SceneMaterial
		subMtls = [s for s in self._nativeSubmaterials() if s]
		return [SceneMaterial(self._scene, mtl) for mtl in subMtls]

	@classmethod
	def fromDictionary(self, dictionary, materialType, mapType):
		"""Create a new material from a dictionary.

		For more information regarding the form the dictionary
		should take, see the documentation for this class's
		__iter__() method.

		Args:
			dictionary(dict): The dictionary containing the material
				description.
			materialType(cross3d.constants.MaterialType): The type of
				material to create.
			mapType(cross3d.constants.MapType): The type of maps to create.

		Returns:
			cross3d.SceneMaterial
		"""
		pass

	@staticmethod
	def fromXml(scene, xml):
		"""Create a new material from the given XML data.

		Args:
			xml(cross3d.migrate.XMLElement): The XML data containing the
				material description.
		
		Returns:
			cross3d.SceneMaterial
		"""
		if (not xml):
			return None
		mname = xml.attribute('name')
		mid = int(xml.attribute('id', 0))
		return scene.findMaterial(mname, mid)

	def __iter__(self):
		"""Makes material objects Python iterables.

		If implemented, this will need to be implemented in concrete
		material classes.  For Materials, this is intended to provide
		a method of creating a generic representation of the material
		structure as a Python dict value.  The structure should look
		like the following:

		{
			name: '<mtlName>',
			objects: ['objectName', ...],
			maps: {'propertyName':'mapPath', ...},
		}

		Where name is the name of this material, objects is a list of
		object names that are using this material, and maps is a dict
		containing key:value pairs for maps referenced by this material
		and the property using them (ie: diffuse, specular, etc).

		Making use of this functionality is as easy as casting the
		material as a dictionary:

			>>> dict(mySceneMaterial)
		"""
		pass

cross3d.registerSymbol('SceneMaterial', AbstractSceneMaterial, ifNotFound=True)

