##
#	\namespace	blur3d.api.abstract.abstractscenepropset
#
#	\remarks	The AbstractScenePropSet defines a class that creates a generic property set of information for any attribute that is being used
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

class AbstractScenePropSet:
	def __init__( self, scene, nativePropSet ):
		# define parameters
		self._scene 		= scene
		self._nativePointer = nativePropSet
	
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
	
	def activateProperty( self, propname, state ):
		"""
			\remarks	[abstract] set the inputed propname as active or not
			\param		propname	<str>
			\param		state		<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		if ( not debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def activeProperties( self ):
		"""
			\remarks	[abstract] return a list of the active property names for this prop set
			\return		<list> [ <str> propname, .. ]
		"""
		from bludev import debug
		
		if ( not debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def propSetName( self ):
		"""
			\remarks	[abstract] return the name for this property set
			\return		<str> name
		"""
		from bludev import debug
		
		if ( not debug.debugLevel() ):
			raise NotImplementedError
		
		return ''
	
	def propSetId( self ):
		"""
			\remarks	[abstract] return the unique id for this property set
			\return		<int> id
		"""
		from bludev import debug
		
		if ( not debug.debugLevel() ):
			raise NotImplementedError
		
		return 0
		
	def isActive( self ):
		"""
			\remarks	return whether or not any property is used in this set
			\return		<bool> used
		"""
		return len(self.activeProperties()) != 0
	
	def isCustomProperty( self, propname ):
		"""
			\remarks	[abstract] return whether or not the inputed property name is a custom property or a standard property
			\param		propname	<str>
			\return		<bool> custom
		"""
		from blurdev import debug
		if ( debug.debugLevel() ):
			raise NotImplementedError
		return False
	
	def isActiveProperty( self, propname ):
		"""
			\remarks	return whether or not the inputed property name is currently being used in this set
			\param		propname	<str>
			\return		<bool> used
		"""
		return str(propname) in self.activeProperties()
	
	def nativePointer( self ):
		"""
			\remarks	return the native wrapper for this instance
			\return		<variant>
		"""
		return self._nativePointer
	
	def propertyNames( self ):
		"""
			\remarks	[abstract] return a list of the property names for this property set
			\return		<list> [ <str> propname, .. ]
		"""
		from blurdev import debug
		if ( debug.debugLevel() ):
			raise NotImplementedError
		return []
	
	def recordXml( self, xml ):
		"""
			\remarks	record this property set to xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', self.propSetName() )
		xml.setAttribute( 'id',		self.propSetId() )
		return True
	
	def setPropSetName( self, propSetName ):
		"""
			\remarks	[abstract] set the name for this property set
			\param		propSetName	<str>
			\return		<bool> success
		"""
		from bludev import debug
		
		if ( not debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setPropSetId( self, propSetId ):
		"""
			\remarks	[abstract] set the unique id for this property set
			\param		propSetId	<int>
			\return		<bool> success
		"""
		from bludev import debug
		
		if ( not debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def setValue( self, propname, value ):
		"""
			\remarks	[abstract] set the value of the property
			\param		propname	<str>
			\param		value		<variant>
			\return		<bool> success
		"""
		from blurdev import debug
		if ( debug.debugLevel() ):
			raise NotImplementedError
		return False
	
	def toolTip( self ):
		"""
			\remarks	[abstract] return the tool tip for this property set based on the usage and value strings
			\return		<str>
		"""
		from blurdev import debug
		if ( debug.debugLevel() ):
			raise NotImplementedError
		return ''
	
	def value( self, propname, default = None ):
		"""
			\remarks	[abstract] return the value for the inputed propname, returining the default value if not found
			\param		propname	<str>
			\param		default		<variant>
			\return		<variant>
		"""
		from blurdev import debug
		if ( debug.debugLevel() ):
			raise NotImplementedError
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
		return scene.findPropSet( propSetName = xml.attribute( 'name' ), propSetId = int(xml.attribute( 'id', 0 )) )

# register the class to the system
from blur3d import api
api.registerSymbol( 'ScenePropSet', AbstractScenePropSet )