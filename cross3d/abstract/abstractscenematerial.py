##
#	\namespace	blur3d.api.abstract.abstractscenematerial
#
#	\remarks	The AbstractSceneMaterial class provides an interface to editing materials in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper

class AbstractSceneMaterial( SceneWrapper ):
	iconCache = {}
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _nativeSubmaterials( self ):
		"""
			\remarks	return the native sub-materials for this material instance
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		return []
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def edit( self ):
		"""
			\remarks	allow the user to edit the material
			\return		<bool> success
		"""
		return False
		
	def icon( self ):
		"""
			\remarks	return the icon for this material type
			\return		<QIcon>
		"""
		return AbstractSceneMaterial.cachedIcon( self.materialType() )
	
	def materialType( self ):
		"""
			\remarks	[virtual] return the material type for this material instance
			\return		<blur3d.constants.MaterialType>
		"""
		from blur3d.constants import MaterialType
		return MaterialType.Generic
	
	def submaterials( self ):
		"""
			\remarks	return a list of the sub-materials for this instance
			\sa			setSubmaterials, _nativeSubmaterials
			\return		<list> [ <blur3d.gui.SceneMaterial>, .. ]
		"""
		from blur3d.api import SceneMaterial
		return [ SceneMaterial( self._scene, mtl ) for mtl in self._nativeSubmaterials() ]
	
	@staticmethod
	def cachedIcon( materialType ):
		icon = AbstractSceneMaterial.iconCache.get( materialType )
		
		# return a cached icon
		if ( icon ):
			return icon
		
		# create an icon cache
		from blur3d.constants 	import MaterialType
		
		# create a default icon
		if ( materialType & MaterialType.Generic ):
			iconfile = 'img/materials/default.png'
		
		# create the QIcon
		import blur3d
		from PyQt4.QtGui 		import QIcon
		icon = QIcon( blur3d.resourcePath( iconfile ) )
		AbstractSceneMaterial.iconCache[ materialType ] = icon
		return icon
	
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	create a new material from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		if ( not xml ):
			return None
		mname 	= xml.attribute( 'name' )
		mid		= int(xml.attribute( 'id', 0 ))
		return scene.findMaterial( mname, mid )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneMaterial', AbstractSceneMaterial, ifNotFound = True )