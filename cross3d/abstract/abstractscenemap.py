##
#	\namespace	cross3d.abstract.abstractscenemap
#
#	\remarks	The AbstractSceneMap class provides an interface to editing maps in a Scene environment for any DCC application
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import SceneWrapper, abstractmethod


class AbstractSceneMap(SceneWrapper):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def edit(self):
		"""Allow the user to edit the map

		"""
		return False

	@staticmethod
	def fromXml(scene, xml):
		"""Create a new map from the inputed xml data
		
		:param xml: :class:`cross3d.migrate.XMLElement`

		"""
		if (xml):
			return scene.findMap(name=xml.attribute('name'), uniqueId=int(xml.attribute('id', 0)))
		return None


# register the symbol
cross3d.registerSymbol('SceneMap', AbstractSceneMap, ifNotFound=True)
