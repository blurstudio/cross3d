##
#	\namespace	blur3d.api.abstract.abstractsceneobjectgroup
#
#	\remarks	The AbstractSceneObjectGroup class provides an interface for working on sets of SceneObject's as a singular group
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d import abstractmethod
from abstractcontainer import AbstractContainer
from blur3d import api

class AbstractGroup(AbstractContainer):
	"""
		The SceneObjectGroup class provides an interface for working on sets of 
		SceneObject's as a singular group
	"""
	
	pass

# register the symbol
api.registerSymbol('Group', AbstractGroup, ifNotFound=True)
