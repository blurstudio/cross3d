##
#	\namespace	blur3d.api.abstract.abstractscenematerial
#
#	\remarks	The AbstractSceneMaterial class provides an interface to editing materials in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blurdev import debug
from abstractscenewrapper import AbstractSceneWrapper

class AbstractSceneMaterial( AbstractSceneWrapper ):
	iconCache = {}
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeSubmaterials( self ):
		"""
			\remarks	[abstract] return the native sub-materials for this material instance
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	[abstract] allow the user to edit the material
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
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