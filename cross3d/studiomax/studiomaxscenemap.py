##
#	\namespace	blur3d.api.abstract.abstractscenemap
#
#	\remarks	The AbstractSceneMap class provides an interface to editing maps in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 										import mxs
from blur3d.api.abstract.abstractscenemap 		import AbstractSceneMap

class StudiomaxSceneMap( AbstractSceneMap ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	implements AbstractSceneMap._nativeProperty to return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		try:
			return self._nativePointer.property( str(key) )
		except:
			return default
		
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	implements AbstractSceneMap._setNativeProperty to set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		try:
			self._nativePointer.setProperty( str( key ), nativeValue )
			return True
		except:
			return False
	
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
	
	def hasProperty( self, key ):
		"""
			\remarks	implements AbstractSceneMap.hasProperty to check to see if the inputed property name exists for this map
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		return mxs.isProperty( self._nativePointer, str(key) ) or mxs.hasProperty( self._nativePointer, str(key) )
	
	def mapName( self ):
		"""
			\remarks	implements AbstractSceneMap.mapName to return the name of this map instance
			\sa			setMapName
			\return		<str> name
		"""
		return self._nativePointer.name
	
	def mapId( self ):
		"""
			\remarks	implements AbstractSceneMap.mapId to return the unique id for this map instance
			\sa			setMapId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )
	
	def setMapName( self, mapName ):
		"""
			\remarks	implements AbstractSceneMap.mapId to set the name of this map instance
			\sa			mapName
			\param		mapName	<str>
			\return		<bool> success
		"""
		self._nativePointer.name = mapName
		return True
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneMap', StudiomaxSceneMap )