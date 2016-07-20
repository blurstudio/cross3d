##
#	\namespace	cross3d.abstract.abstractscenepropset
#
#	\remarks	The AbstractScenePropSet defines a class that creates a generic property set of information for any attribute that is being used
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import SceneWrapper, abstractmethod


class AbstractScenePropSet(SceneWrapper):
	"""
	The ScenePropSet defines a class that creates a generic property set 
	of information for any attribute that is being used
	"""

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def activateProperties(self, state):
		"""
		Set the usage state for all properties to true
		
		:param state: bool
		:return: bool
		"""
		for propname in self.propertyNames():
			self.activateProperty(propname, state)
		return True

	@abstractmethod
	def activateProperty(self, propname, state):
		"""Set the inputed propname as active or not
		
		:param propname: str
		:param state: bool
		:return: bool
		
		"""
		return False

	@abstractmethod
	def activeProperties(self):
		"""
		Return a list of the active property names for this prop set
		
		:return: a list of strings (propnames)
		
		"""
		return False

	def isActive(self):
		"""
		Return whether or not any property is used in this set
		
		:return: bool
		
		"""
		return len(self.activeProperties()) != 0

	@abstractmethod
	def isCustomProperty(self, propname):
		"""
		Return whether or not the inputed property name is a custom 
		property or a standard property
		
		:param propname: str
		:return: bool
		
		"""
		return False

	def isActiveProperty(self, propname):
		"""
		Teturn whether or not the inputed property name is currently 
		being used in this set
		
		:param propname: str
		:return: bool

		"""
		return str(propname) in self.activeProperties()

	@abstractmethod
	def propertyNames(self):
		"""
		Return a list of the property names for this property set
		
		:return: a list of strings (propnames)
		
		"""
		return []

	@abstractmethod
	def setValue(self, propname, value):
		"""Set the value of the property
		
		"""
		return False

	@abstractmethod
	def toolTip(self):
		"""
		Return the tool tip for this property set based on the usage 
		and value strings

		"""
		return ''

	@abstractmethod
	def value(self, propname, default=None):
		"""
		Return the value for the inputed propname, returining the 
		default value if not found

		"""
		return default

	@staticmethod
	def fromXml(scene, xml):
		"""
		Restores a property set from the scene based on the inputed xml
		
		:param scene: :class:`cross3d.Scene`
		:param xml: :class:`cross3d.migrate.XMLElement`
		:return: :class:`cross3d.classes.ScenePropSet` or None
		
		"""
		if (not xml):
			return None
		return scene.findPropSet(name=xml.attribute('name'), uniqueId=int(xml.attribute('id', 0)))


# register the class to the system
cross3d.registerSymbol('ScenePropSet', AbstractScenePropSet)
cross3d.registerSymbol('SceneObjectPropSet', AbstractScenePropSet)

