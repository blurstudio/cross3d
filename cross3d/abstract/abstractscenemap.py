##
#	\namespace	blur3d.api.abstract.abstractscenemap
#
#	\remarks	The AbstractSceneMap class provides an interface to editing maps in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper

class AbstractSceneMap( SceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def edit( self ):
		"""
			\remarks	allow the user to edit the map
			\return		<bool> success
		"""
		return False
		
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	create a new map from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		if ( xml ):
			return scene.findMap( name = xml.attribute( 'name' ), uniqueId = int(xml.attribute( 'id', 0 )) )
		return None
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneMap', AbstractSceneMap, ifNotFound = True )
