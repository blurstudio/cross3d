##
#	\namespace	blur3d.api.softimage.softimagegroup
#
#	\remarks	The SoftimageSceneObjectGroup class provides an interface for working with Softimage groups.
#	
#	\author		douglas@blur.com
#	\author		Blur Studio 
#	\date		09/20/13
#

from PySoftimage import xsi
from blur3d.api.abstract.abstractgroup import AbstractGroup

class SoftimageGroup(AbstractGroup):
	"""
		The SoftimageSceneObjectGroup class provides an interface for working with Softimage groups.
	"""
	
	_groupOptionsIn = {0:2, 1:0, 2:1}
	_groupOptionsOut = {2:0, 0:1, 1:2}
	
	def _nativeObjects(self):
		"""
			\remarks	return a list of the native objects that are currently on this group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return self._nativeGroup.Members
		
	def isHidden(self):
		return self._groupOptionsOut[ self._nativePointer.viewvis.Value ]

	def isFrozen(self):
		return self._groupOptionsOut[ self._nativePointer.selectability.Value ]
		
	def toggleHidden(self):
		hidden = not self._nativePointer.viewvis.Value
		self._nativePointer.viewvis.Value = hidden
		self._nativePointer.rendvis.Value = hidden
		xsi.SceneRefresh()
		return True
		
	def toggleFrozen(self):
		self._nativePointer.selectability = not self._nativePointer.selectability
		xsi.SceneRefresh()
		return True

	def setHidden(self, hidden):
		hidden = self._groupOptionsIn[hidden]
		self._nativePointer.viewvis.Value = hidden
		self._nativePointer.rendvis.Value = hidden
		xsi.SceneRefresh()
		return True

	def setFrozen(self, frozen):
		self._nativePointer.selectability.Value = self._groupOptionsIn[frozen]
		xsi.SceneRefresh()
		return True

# register the symbol
from blur3d import api
api.registerSymbol('Group', SoftimageGroup)

