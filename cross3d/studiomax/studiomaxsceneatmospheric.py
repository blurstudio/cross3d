##
#	\namespace	blur3d.api.abstract.abstractsceneatmospheric
#
#	\remarks	The AbstractSceneAtmospheric class provides an interface to editing atmospherics in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 										import mxs
from blur3d.api.abstract.abstractsceneatmospheric	import AbstractSceneAtmospheric

class StudiomaxSceneAtmospheric( AbstractSceneAtmospheric ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeLayer( self ):
		"""
			\remarks	implements AbstractSceneAtmospheric._nativeLayer method to return the native layer instance for this atmospheric
			\return		<Py3dsMax.mxs.Layer> || None
		"""
		return self.layer().nativePointer()
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def name( self ):
		"""
			\remarks	implements AbstractSceneWrapper.name to return the name of this atmospheric instance
			\sa			setName
			\return		<str> name
		"""
		return self._nativePointer.name
	
	def isEnabled( self ):
		"""
			\remarks	implements AbstractSceneAtmospheric.isEnabled method to check if this atmospheric is enabled in the scene
			\return		<bool> enabled
		"""
		return mxs.isActive( self._nativePointer )
	
	def layer( self ):
		"""
			\remarks	reimplements AbstractSceneAtmospheric.layer to return the layer that this atmospheric is associated with
			\return		<blur3d.api.Layer> || None
		"""
		layers 	= self._scene.layers()
		uid		= mxs.blurUtil.uniqueId( self._nativePointer )
		for l in layers:
			atm = list(l.metaData().value('linkedAtmos'))
			if ( uid in atm ):
				return l
		return None
	
	def setName( self, name ):
		"""
			\remarks	implements AbstractSceneWrapper.setName to set the name of this atmosepheric instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		self._nativePointer.name = name
		return True
	
	def setEnabled( self, state ):
		"""
			\remarks	implements AbstractSceneAtmospheric.setEnabled method to set this atmospheric enabled in the scene
			\param		state	<bool>
			\return		<bool> success
		"""
		mxs.setActive( self._nativePointer, state )
		return True
		
	def uniqueId( self ):
		"""
			\remarks	implements AbstractSceneWrapper.uniqueId to return the unique id for this atmospheric instance
			\sa			setUniqueId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAtmospheric', StudiomaxSceneAtmospheric )