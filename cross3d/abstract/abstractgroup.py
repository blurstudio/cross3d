##
#	\namespace	cross3d.abstract.abstractsceneobjectgroup
#
#	\remarks	The AbstractSceneObjectGroup class provides an interface for working on sets of SceneObject's as a singular group
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from cross3d import abstractmethod
from abstractcontainer import AbstractContainer
import cross3d

class AbstractGroup(AbstractContainer):

	"""
		A group is an object that allows to manipulate several objects at once.
		When it's possible a group has a native equivalent. See the various implementations for details.
	"""
	
	@abstractmethod	
	def _nativeObjects(self):
		return []
	
	@abstractmethod	
	def isHidden(self):
		return False

	@abstractmethod	
	def isFrozen(self):
		return False
	
	@abstractmethod		
	def toggleHidden(self):
		return False
		
	@abstractmethod	
	def toggleFrozen(self):
		return False

	@abstractmethod	
	def setHidden(self, hidden, options=None, affectObjects=False):
		return False

	@abstractmethod	
	def setFrozen(self, frozen, affectObjects=False):
		return False

	@abstractmethod	
	def name(self):
		return ''

# register the symbol
cross3d.registerSymbol('Group', AbstractGroup, ifNotFound=True)
