##
#	\namespace	blur3d.api.abstract.abstractscenemodel
#
#	\remarks	The AbstractSceneModel class provides the base foundation for the 3d Object framework for the blur3d system
#				This class will provide a generic overview structure for all manipulations of 3d models
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/05/10 
#

from blur3d import abstractmethod
from blur3d.api import SceneObject, Group
from blur3d.constants import ObjectType
from blur3d import api

class AbstractSceneModel(SceneObject):
	"""
		The SceneModel class provides the base foundation for the 3d Object 
		framework for the blur3d system.  This class will provide a generic 
		overview structure for all manipulations of 3d models
	"""

	_objectType = ObjectType.Model

	#--------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#--------------------------------------------------------------------------------------------------------------------

	@abstractmethod
	def _nativeGroups(self, wildcard='*'):
		return []

	@abstractmethod
	def isReferenced(self):
		return False
		
	def objects(self, wildcard='', type=''):
		return self.children(recursive=True, wildcard=wildcard, type=type)

	def groups(self, wildcard='*'):
		groups = []
		for nativeGroup in self._nativeGroups(wildcard):
			groups.append(Group(self._scene, nativeGroup))
		return groups
		
	@abstractmethod
	def export(self, fileName):
		return False

	@abstractmethod
	def update(self):
		return False

	@abstractmethod
	def offloaded(self):
		return False
		
	@abstractmethod
	def offload(self):
		return False

	@abstractmethod
	def addResolution(self, name='', path='', load=False):
		return False

	@abstractmethod
	def removeResolution(self, name):
		return False

	@abstractmethod
	def resolutionPath(self, name=''):
		return ''

	@abstractmethod
	def setResolutionPath(self, path, name=''):
		return False

	@abstractmethod
	def setResolution(self, name):
		return False

	@abstractmethod
	def resolution(self):
		return ''

	@abstractmethod
	def resolutions(self):
		return []
	
	@abstractmethod
	def addAnimationClip(self, path, name=None):
		return False
	

# register the symbol
api.registerSymbol('SceneModel', AbstractSceneModel, ifNotFound=True)
