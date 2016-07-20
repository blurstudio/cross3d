##
#	\namespace	cross3d.softimage.softimagegroup
#
#	\remarks	The SoftimageSceneObjectGroup class provides an interface for working with Softimage groups.
#	
#	\author		douglas
#	\author		Blur Studio 
#	\date		09/20/13
#

from PySoftimage import xsi
from cross3d import application
from cross3d.abstract.abstractgroup import AbstractGroup

class SoftimageGroup(AbstractGroup):

	"""
		This class provide an interface for Softimage's native groups.
		Native groups in Softimage are explorable and non-transformable objects scene objects as members.
	"""
	
	_groupOptionsIn = {0:2, 1:0, 2:1}
	_groupOptionsOut = {2:0, 0:1, 1:2}
	
	def _nativeObjects(self):
		"""
			\remarks	return a list of the native objects that are currently on this group
			\sa			objects
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return self._nativePointer.Members
		
	def isHidden(self):
		return self._groupOptionsOut[ self._nativePointer.viewvis.Value ]

	def isFrozen(self):
		return self._groupOptionsOut[ self._nativePointer.selectability.Value ]
		
	def toggleHidden(self):
		hidden = not self._nativePointer.viewvis.Value
		self._nativePointer.viewvis.Value = hidden
		self._nativePointer.rendvis.Value = hidden
		application.refresh()
		return True
		
	def toggleFrozen(self):
		self._nativePointer.selectability = not self._nativePointer.selectability
		application.refresh()
		return True

	def setHidden(self, hidden, options=None, affectObjects=False):
		hidden = self._groupOptionsIn[hidden]
		self._nativePointer.viewvis.Value = hidden
		self._nativePointer.rendvis.Value = hidden
		application.refresh()
		return True

	def setFrozen(self, frozen, affectObjects=False):
		self._nativePointer.selectability.Value = self._groupOptionsIn[frozen]
		application.refresh()
		return True

	def name(self):
		return self._nativePointer.FullName

# register the symbol
import cross3d
cross3d.registerSymbol('Group', SoftimageGroup)

