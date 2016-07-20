##
#	\namespace	cross3d.studiomax.studiomaxscenefx
#
#	\remarks	The StudiomaxSceneFx class provides an interface to editing fx in a Scene environment for 3dsMax
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax import mxs
from cross3d.abstract.abstractscenefx import AbstractSceneFx

class StudiomaxSceneFx( AbstractSceneFx ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeLayer( self ):
		"""
			\remarks	implements AbstractSceneFx._nativeLayer method to return the native layer instance for this fx
			\return		<Py3dsMax.mxs.Layer> || None
		"""
		return self.layer().nativePointer()
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def name( self ):
		"""
			\remarks	implements AbstractSceneWrapper.name to return the name of this fx instance
			\sa			setName
			\return		<str> name
		"""
		if hasattr(self._nativePointer, 'name'):
			return self._nativePointer.name
		else:
			return None
	
	def isEnabled( self ):
		"""
			\remarks	implements AbstractSceneFx.isEnabled method to check if this fx is enabled in the scene
			\return		<bool> enabled
		"""
		return True
	
	def layer( self ):
		"""
			\remarks	reimplements AbstractSceneFx.layer to return the layer that this fx is associated with
			\return		<cross3d.Layer> || None
		"""
		layers 	= self._scene.layers()
		uid		= mxs.blurUtil.uniqueId( self._nativePointer )
		for l in layers:
			atm = list(l.metaData().value('linkedFx'))
			if ( uid in atm ):
				return l
		return None
	
	def setName( self, name ):
		"""
			\remarks	implements AbstractSceneWrapper.setName to set the name of this fx instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		if hasattr(self._nativePointer, 'name'):
			self._nativePointer.name = name
			return True
		else:
			return False
	
	def setEnabled(self, state, ids=[]):
		"""
			\remarks	this is a no-op since there doesn't appear to be a way to affect dynamics object this way.
			\param		state	<bool>
			\return		<bool> success
		"""
		mxs.cross3dhelper.toggleSubDyn(self.nativePointer(), state)
		
	def uniqueId( self ):
		"""
			\remarks	implements AbstractSceneWrapper.uniqueId to return the unique id for this fx instance
			\sa			setUniqueId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )
		
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneFx', StudiomaxSceneFx )

