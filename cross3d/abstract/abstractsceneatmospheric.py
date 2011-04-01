##
#	\namespace	blur3d.api.abstract.abstractsceneatmospheric
#
#	\remarks	The AbstractSceneAtmospheric class provides an interface to editing atmosperhics in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper

class AbstractSceneAtmospheric( SceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _nativeLayer( self ):
		"""
			\remarks	return the layer that this atmospheric is a part of
			\sa			layer
			\return		<variant> nativeLayer || None
		"""
		return None
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def disable( self ):
		"""
			\remarks	disables this atmospheric in the scene
			\sa			enable, isEnabled, setEnabled
			\return		<bool> success
		"""
		return self.setEnabled( False )
	
	def enable( self ):
		"""
			\remarks	enables this atmospheric in the scene
			\sa			disable, isEnabled, setEnabled
			\return		<bool> success
		"""
		return self.setEnabled( True )
	
	@abstractmethod
	def isEnabled( self ):
		"""
			\remarks	return whether or not this atmospheric is currently enabled in the scene
			\sa			disable, enable, setEnabled
			\return		<bool> enabled
		"""
		return False
	
	def layer( self ):
		"""
			\remarks	return the layer that this atmospheric is a part of
			\return		<blur3d.api.SceneLayer> || None
		"""
		nativeLayer = self._nativeLayer()
		if ( nativeLayer ):
			from blur3d.api import SceneLayer
			return SceneLayer( self._scene, nativeLayer )
		return None
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this atmospheric is linked to
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	@abstractmethod
	def setEnabled( self, state ):
		"""
			\remarks	set whether or not this atmospheric is currently enabled in the scene
			\sa			disable, enable, isEnabled
			\param		state		<bool>
			\return		<bool> success
		"""
		return False
		
	@classmethod
	def fromXml( cls, scene, xml ):
		"""
			\remarks	restore the atmospheric from the inputed xml node
			\param		scene	<blur3d.api.Scene>
			\param		xml		<blurdev.XML.XMLElement>
			\return		<blurdev.api.SceneAtmospheric> || None
		"""
		return scene.findAtmospheric( name = xml.attribute( 'name' ), uniqueId = int(xml.attribute('id',0)) )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAtmospheric', AbstractSceneAtmospheric, ifNotFound = True )