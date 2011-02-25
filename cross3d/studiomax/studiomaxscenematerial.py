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
	
	def name( self ):
		"""
			\remarks	implements AbstractSceneMaterial.name to return the name of this material instance
			\sa			setName
			\return		<str> name
		"""
		return self._nativePointer.name
	
	def setName( self, name ):
		"""
			\remarks	implements AbstractSceneMaterial.setName to set the name of this material instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		self._nativePointer.name = name
		return True
		
	def uniqueId( self ):
		"""
			\remarks	implements AbstractSceneMaterial.uniqueId to return the unique id for this material instance
			\sa			setUniqueId
			\return		<int> id
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneMaterial', StudiomaxSceneMaterial )