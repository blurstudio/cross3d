##
#   \namespace  cross3d.abstract.collection
#
#   \remarks    This module implements the collection class allowing to manipulate multiple objects.
#
#   \author     douglas
#   \author     Blur Studio
#   \date       04/20/15
#

#-------------------------------------------------------------------------

import cross3d
from cross3d import abstractmethod
from collections import MutableSequence

class Collection(MutableSequence):

	""" 
		The Collection object allows to perform operation on several objects at once
		allowing to optimize the process and lift weight from the Scene object.
	"""

	# ----------------------------------------------

	# TODO: Implement that block.

	def __setitem__(self, index, item):
		pass

	def __delitem__(self, index):
		pass

	def __len__(self):
		pass

	def insert(self, index, item):
		pass
		
	# ----------------------------------------------

	@classmethod
	def _objectsGenerator(cls, scene, objects):
		for obj in objects:
			if isinstance(obj, cross3d.SceneObject):
				yield obj
			else:
				yield cross3d.SceneObject(scene, obj)

	@classmethod
	def _nativeObjectsGenerator(cls, objects):
		for obj in objects:
			if isinstance(obj, cross3d.SceneObject):
				yield obj()
			else:
				yield obj

	def __init__(self, scene, objects):
		self._scene = scene
		self._objects = self._objectsGenerator(scene, objects)
		self._nativeObjects = self._nativeObjectsGenerator(objects)
		super(Collection, self).__init__()

	@abstractmethod
	def setHidden(self, hidden):
		return False

# Registering the symbol.
cross3d.registerSymbol('Collection', Collection)
