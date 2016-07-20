##
#	\namespace	cross3d.abstract.abstractscenecache
#
#	\remarks	The AbstractSceneCache class provides an interface to editing data caches in a Scene environment for any DCC application
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import SceneWrapper, abstractmethod


class AbstractSceneCache(SceneWrapper):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def disable(self):
		"""Convenience method for disabling this cache in the scene

		"""
		return self.setEnabled(False)

	def controllers(self):
		"""Return a list of the controllers that are currently on this 
		cache instance
		
		:return: a list of :class:`cross3d.SceneAnimationController`'s
			
		"""
		from cross3d import SceneAnimationController
		return [ SceneAnimationController(self._scene, nativeControl) for nativeControl in self._nativeControllers() ]

	def enable(self):
		"""Convenience method for enabling this cache in the scene

		"""
		return self.setEnabled(True)

	@abstractmethod
	def filename(self):
		"""Return the filename that this cache is pulling from
			
		"""
		return ''

	@abstractmethod
	def isEnabled(self):
		"""Return wether or not this cache is enabled in the scene
			
		"""
		return False

	@abstractmethod
	def setEnabled(self, state):
		"""Mark whether or not this cache is enabled in the scene

		"""
		return False

	@abstractmethod
	def setFilename(self, filename):
		"""Set the filename for this cache data to the inputed filename

		"""
		return False


# register the symbol
cross3d.registerSymbol('SceneCache', AbstractSceneCache, ifNotFound=True)
