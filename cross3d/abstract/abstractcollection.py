##
#	\namespace	blur3d.api.abstract.abstractcollection
#
#	\remarks	The Collection object allows to perform operation on several objects at once
#				allowing to optimize the process and lift weight from the Scene object.
#	
#	\author		douglas@blur.com
#	\author		Blur Studio 
#	\date		09/20/13
#

from blur3d import abstractmethod
from blur3d import api

class AbstractCollection(list):
	"""
		The Collection object allows to perform operation on several objects at once
		allowing to optimize the process and lift weight from the Scene object.
	"""
	def __init__(self, nativePointer):
		self._nativePointer = nativePointer

	def unhide(self):
		return self.setVisible(True)
		
	def hide(self):
		return self.setVisible(False)
		
	def freeze(self):
		return self.setFrozen(True)
	
	def unfreeze(self):
		return self.setFrozen(False)
		
	@abstractmethod
	def key(self):
		return False

	@abstractmethod
	def select(self):
		return False
		
	@abstractmethod
	def setHidden(self, visibility):
		return False

	@abstractmethod
	def setFrozen(self, selectability):
		return False

	@abstractmethod
	def resetTransforms(self, pos=True, rot=True, scl=True):
		return False

# register the symbol
api.registerSymbol('Collection', AbstractCollection, ifNotFound=True)

