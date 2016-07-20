##
#	\namespace	cross3d.softimage.softimagescenewrapper
#
#	\remarks	The AbstractSceneWrapper class defines the base class for all other scene wrapper instances.  This creates a basic wrapper
#				class for mapping native object instances from a DCC application to the cross3d structure
#
#	\author		douglas
#	\author		Blur Studio
#	\date		04/04/11
#

from PySoftimage import xsi, constants as xsiConstants
from cross3d.abstract.abstractscenewrapper 	import AbstractSceneWrapper

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneWrapper( AbstractSceneWrapper ):
	def __eq__(self, other):
		if isinstance(other, AbstractSceneWrapper):
			return self.nativePointer().IsEqualTo(other.nativePointer())
		return False
	
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	implements the AbstractSceneWrapper._nativeProperty method to return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		return self._nativePointer.Properties[key]
#		return xsi.GetValue( '%s.%s' % (self._nativePointer.fullname, key) )
	
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	implements the AbstractSceneWrapper._setNativeProperty method to set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		xsi.SetValue('%s.%s' % (self._nativePointer.fullname, key), nativeValue)
		return True

	def setDisplayName( self, name ):
		"""
			\remarks	set the name of this wrapper instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		# NOTE: passing a PyQt4.QtCore.QString object will crash Softimage
		self.nativePointer().Name = unicode(name)
		return True

	def name( self ):
		return self._nativePointer.FullName
	
	def displayName( self ):
		return self._nativePointer.Name
	
	def propertyNames(self):
		return [prop.name for prop in self._nativePointer.Properties]
	
	def hasProperty(self, key):
		return (key in self.propertyNames())

	def isReferenced(self):
		return self._nativePointer.Model.ModelKind == xsiConstants.siModelKind_Reference

# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneWrapper', SoftimageSceneWrapper )
