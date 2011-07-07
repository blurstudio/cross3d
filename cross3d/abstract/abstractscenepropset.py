##
#	\namespace	blur3d.api.abstract.abstractscenepropset
#
#	\remarks	The AbstractScenePropSet defines a class that creates a generic property set of information for any attribute that is being used
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper

class AbstractScenePropSet( SceneWrapper ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def activateProperties( self, state ):
		"""
			\remarks	set the usage state for all properties to true
			\param		state	<bool>
			\return		<bool> success
		"""
		for propname in self.propertyNames():
			self.activateProperty( propname, state )
		return True
	
	@abstractmethod
	def activateProperty( self, propname, state ):
		"""
			\remarks	set the inputed propname as active or not
			\param		propname	<str>
			\param		state		<bool>
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def activeProperties( self ):
		"""
			\remarks	return a list of the active property names for this prop set
			\return		<list> [ <str> propname, .. ]
		"""
		return False
	
	def isActive( self ):
		"""
			\remarks	return whether or not any property is used in this set
			\return		<bool> used
		"""
		return len(self.activeProperties()) != 0
	
	@abstractmethod
	def isCustomProperty( self, propname ):
		"""
			\remarks	return whether or not the inputed property name is a custom property or a standard property
			\param		propname	<str>
			\return		<bool> custom
		"""
		return False
	
	def isActiveProperty( self, propname ):
		"""
			\remarks	return whether or not the inputed property name is currently being used in this set
			\param		propname	<str>
			\return		<bool> used
		"""
		return str(propname) in self.activeProperties()
	
	@abstractmethod
	def propertyNames( self ):
		"""
			\remarks	return a list of the property names for this property set
			\return		<list> [ <str> propname, .. ]
		"""
		return []
	
	@abstractmethod
	def setValue( self, propname, value ):
		"""
			\remarks	set the value of the property
			\param		propname	<str>
			\param		value		<variant>
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def toolTip( self ):
		"""
			\remarks	return the tool tip for this property set based on the usage and value strings
			\return		<str>
		"""
		return ''
	
	@abstractmethod
	def value( self, propname, default = None ):
		"""
			\remarks	return the value for the inputed propname, returining the default value if not found
			\param		propname	<str>
			\param		default		<variant>
			\return		<variant>
		"""
		return default
	
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	restores a property set from the scene based on the inputed xml
			\param		scene	<blur3d.api.Scene>
			\param		xml		<blurdev.XML.XMLElement>
			\return		<blur3d.classes.ScenePropSet> || None
		"""
		if ( not xml ):
			return None
		return scene.findPropSet( name = xml.attribute( 'name' ), uniqueId = int(xml.attribute( 'id', 0 )) )

# register the class to the system
from blur3d import api
api.registerSymbol( 'ScenePropSet', AbstractScenePropSet )