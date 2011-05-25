##
#	\namespace	blur3d.api.softimage.softimagesceneobjectdogTag
#
#	\remarks	The SoftimageSceneObjectMetadata class provides the implementation of the AbstractSceneObjectDogTag class as it applies
#				to Softimage
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/05/11
#

from PySoftimage import xsi

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneObjectMetadata( object ): #not in abstract
	def __init__( self, object ):
		self.obj = object
		self._attributes = {}
		self.property = self.obj._nativePointer.Properties( "Metadata" )
		if self.property:
			self._attributes = eval( self.property.Value )

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def attribute( self, attribute ): #not in abstract
		if self._attributes.has_key( attribute ):
			return self._attributes[ attribute ]
		else:
			return None
	
	def attributes( self ): #not in abstract
		return self._attributes

	def setAttribute( self, attribute, value ):
		if not self.property:
			self.property = self.obj.nativePointer().AddProperty( "UserDataBlob", False, "Metadata" )
		self._attributes[ attribute ] = value
		self.property.Value = str( self._attributes )
		
	def setAttributes( self, **attributes ):
		if not self.property:
			self.property = self.obj.nativePointer().AddProperty( "UserDataBlob", False, "Metadata" )
		for attribute in attributes.keys():
			self._attributes[ attribute ] = attributes[ attribute ]
		self.property.Value = str( self._attributes )
				
	def deleteAttributes( self, *attributes ): #not in abstract
		for attribute in attributes:
			if self._attributes.has_key( attribute ):
				del self._attributes[ attribute ]
		self.property.Value = str( self._attributes )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObjectMetadata', SoftimageSceneObjectMetadata )
		
		
		
		
		