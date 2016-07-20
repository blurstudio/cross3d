##
#	\namespace	cross3d.abstract.abstractscenemap
#
#	\remarks	The AbstractSceneMap class provides an interface to editing maps in a Scene environment for any DCC application
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 										import mxs
from cross3d.abstract.abstractscenemap 		import AbstractSceneMap

class StudiomaxSceneMap( AbstractSceneMap ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	implements AbstractSceneMap.edit to allow the user to edit the map
			\return		<bool> success
		"""
		medit = mxs.medit
		medit.PutMtlToMtlEditor( self._nativePointer, medit.GetActiveMtlSlot() )
		mxs.matEditor.open()
		return True
	
	def name( self ):
		"""
			\remarks	implements AbstractSceneMap.name to return the name of this map instance
			\sa			setName
			\return		<str> name
		"""
		return self._nativePointer.name
	
	def setName( self, name ):
		"""
			\remarks	implements AbstractSceneMap.setName to set the name of this map instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		self._nativePointer.name = name
		return True
		
	def uniqueId( self ):
		"""
			\remarks	implements AbstractSceneMap.uniqueId to return the unique id for this map instance
			\sa			setUniqueId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )
	
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneMap', StudiomaxSceneMap )
