##
#	\namespace	blur3d.api.abstract.abstractscenematerial
#
#	\remarks	The AbstractSceneMaterial class provides an interface to editing materials in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 										import mxs
from blur3d.api.abstract.abstractscenematerial 	import AbstractSceneMaterial

class StudiomaxSceneMaterial( AbstractSceneMaterial ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	implements AbstractSceneMaterial._nativeProperty to return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		try:
			return self._nativePointer.property( str(key) )
		except:
			return default
		
	def _nativeSubmaterials( self ):
		"""
			\remarks	implements AbstractSceneMaterial._nativeSubmaterials method to return the a list of the sub-materials for this material instance
			\return		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
		"""
		mtl		= self._nativePointer
		
		# processing multi/sub materials directly is faster than the getnumsubs system
		if ( mxs.classof( mtl ) == mxs.MultiMaterial ):
			return [ mtl[i] for i in range( mtl.numsubs ) ]
		
		# process all other kinds of materials
		else:
			get_submtl 	= mxs.getSubMtl
			return [ get_submtl(mtl, i+1) for i in range(mxs.getNumSubMtls( mtl )) ]
			
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	implements AbstractSceneMaterial._setNativeProperty to set the value of the property defined by the inputed key
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
			\remarks	implements AbstractSceneMaterial.edit to allow the user to edit the material
			\return		<bool> success
		"""
		medit = mxs.medit
		medit.PutMtlToMtlEditor( self._nativePointer, medit.GetActiveMtlSlot() )
		mxs.matEditor.open()
		return True
	
	def hasProperty( self, key ):
		"""
			\remarks	implements AbstractSceneMaterial.hasProperty to check to see if the inputed property name exists for this material
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		return mxs.isProperty( self._nativePointer, str(key) ) or mxs.hasProperty( self._nativePointer, str(key) )
	
	def materialName( self ):
		"""
			\remarks	implements AbstractSceneMaterial.materialName to return the name of this material instance
			\sa			setMaterialName
			\return		<str> name
		"""
		return self._nativePointer.name
	
	def materialId( self ):
		"""
			\remarks	implements AbstractSceneMaterial.materialId to return the unique id for this material instance
			\sa			setMaterialId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )
	
	def setMaterialName( self, materialName ):
		"""
			\remarks	implements AbstractSceneMaterial.materialId to set the name of this material instance
			\sa			materialName
			\param		materialName	<str>
			\return		<bool> success
		"""
		self._nativePointer.name = materialName
		return True
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneMaterial', StudiomaxSceneMaterial )