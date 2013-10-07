##
#	\namespace	blur3d.api.abstract.abstractscenematerial
#
#	\remarks	The AbstractSceneMaterial class provides an interface to editing materials in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d import abstractmethod
from blur3d.api import SceneWrapper
from blur3d import api


class AbstractSceneMaterial(SceneWrapper):
	iconCache = {}
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _nativeSubmaterials(self):
		"""
			\remarks	return the native sub-materials for this material instance
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		return []

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def edit(self):
		"""Allow the user to edit the material

		"""
		return False

	def icon(self):
		"""Return the icon for this material type
		
		:rtype: :class:`PyQt4.QtGui.QIcon`
		
		"""
		return AbstractSceneMaterial.cachedIcon(self.materialType())

	def materialType(self):
		"""Return the material type for this material instance
		
		:rtype: :data:`blur3d.constants.MaterialType`

		"""
		from blur3d.constants import MaterialType
		return MaterialType.Generic

	def submaterials(self):
		"""Return a list of the sub-materials for this instance
		
		:return: a list of :class:`blur3d.api.SceneMaterial` objects

		"""
		from blur3d.api import SceneMaterial
		subMtls = [s for s in self._nativeSubmaterials() if s]
		return [ SceneMaterial(self._scene, mtl) for mtl in subMtls ]

	@staticmethod
	def cachedIcon(materialType):
		icon = AbstractSceneMaterial.iconCache.get(materialType)

		# return a cached icon
		if (icon):
			return icon

		# create an icon cache
		from blur3d.constants 	import MaterialType

		# create a default icon
		if (materialType & MaterialType.Generic):
			iconfile = 'img/materials/default.png'

		# create the QIcon
		import blur3d
		from PyQt4.QtGui 		import QIcon
		icon = QIcon(blur3d.resourcePath(iconfile))
		AbstractSceneMaterial.iconCache[ materialType ] = icon
		return icon

	@staticmethod
	def fromXml(scene, xml):
		"""Create a new material from the inputed xml data
		
		:param xml: :class:`blurdev.XML.XMLElement`

		"""
		if (not xml):
			return None
		mname 	 = xml.attribute('name')
		mid		 = int(xml.attribute('id', 0))
		return scene.findMaterial(mname, mid)


# register the symbol
api.registerSymbol('SceneMaterial', AbstractSceneMaterial, ifNotFound=True)

