##
#	\namespace	cross3d.studiomax.studiomaxscenepropset
#
#	\remarks	The StudiomaxScenePropSet class defines the different property sets that are used in the Studiomax system.  Since Studiomax
#				does not have a native Property Set instance, we will have to control all of the data ourselves
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax import mxs
from cross3d.abstract.abstractscenepropset	import AbstractScenePropSet

class StudiomaxScenePropSet( AbstractScenePropSet ):
	def __eq__( self, other ):
		if ( isinstance( other, StudiomaxScenePropSet ) ):
			return self.uniqueId() == other.uniqueId()
		return False
		
	def __init__( self, scene, nativePropSet ):
		# in Max, since we don't have native property sets, we'll store a pointer to this self as the native pointer
		AbstractScenePropSet.__init__( self, scene, self )
		
		# we will control property sets
		self._keys 			= []
		self._values 		= {}
		self._active		= {}
		self._custom		= {}
		self._name			= 'Property Set'
		self._uniqueId		= mxs.blurUtil.genUniqueId()
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _activeString( self ):
		"""
			\remarks	converts the current key/active pairing to a string separated by '|'
			\return		<str>
		"""
		output = []
		for key in self._keys:
			if ( self.isActiveProperty(key) ):
				output.append( '1' )
			else:
				output.append( '0' )
		return '|'.join( output )
	
	def _defineProperty( self, propname, value, custom = False ):
		"""
			\remarks	define the inputed propname with the current value, tagging whether or not it is a custom property
			\param		propname	<str>
			\param		value		<variant>
			\param		custom		<bool>
		"""
		propname = str( propname )
		
		# record the property
		self._keys.append( propname )
		self._active[propname] = False	
		self._values[ propname ] = value
		self._custom[ propname ] = custom
	
	def _setActiveString( self, activeString ):
		"""
			\remarks	set the active values for these properties by the inputed value string, which contains a true/false flag per property separated by a '|'
			\param		activeString		<str>
			\return		<bool> success
		"""
		actives = str(activeString).split( '|' )
		for index, key in enumerate(self._keys):
			try:
				self.activateProperty( key, actives[index] == '1' )
			except:
				break
		return True
	
	def _setValueString( self, valueString ):
		"""
			\remarks	sets the value for these properties by the inputed value string, which contains the properties with a '|' separating the values
			\param		valueString		<str>
			\return		<bool> success
		"""
		values = str(valueString).split( '|' )
		for index, key in enumerate(self._keys):
			try:
				self.setValue( key, eval(values[index]) )
			except:
				break
		return True
		
	def _valueString( self ):
		"""
			\remarks	returns the current key/value pairing to a string separated by '|'
			\return		<str>
		"""
		output = []
		for key in self._keys:
			output.append( str(self.value(key)) )
		return '|'.join( output )
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def activateProperty( self, propname, state ):
		self._active[propname] = state
	
	def activeProperties( self ):
		return [ propname for propname in self._active if self._active[propname] ]
	
	def isCustomProperty( self, propname ):
		return self._custom.get(str(propname),False)
	
	def propertyNames( self ):
		return self._keys
	
	def name( self ):
		return self._name
	
	def setName( self, name ):
		self._name = name
	
	def setUniqueId( self, uniqueId ):
		self._uniqueId = uniqueId
	
	def setValue( self, propname, value ):
		propname = str(propname)
		if ( propname in self._values ):
			self._values[propname] = value
			return True
		return False
	
	def toolTip( self ):
		tips = {}
		for key, active in self._active.items():
			if ( active ):
				tips[key] = '%s: %s' % (key,self.value(key))
		tips['id'] = 'ID: {id}'.format(id=str(self.uniqueId()))
		keys = tips.keys()
		keys.sort()
		
		return ', '.join( [ tips[key] for key in keys ] )
	
	def uniqueId( self ):
		return self._uniqueId
	
	def value( self, propname, default = None ):
		return self._values.get( str(propname), default )
	
	@staticmethod
	def fromXml( scene, xml ):
		if ( not xml ):
			return None
			
		propset = StudiomaxScenePropSet( scene, None )
		propset.setName( xml.attribute( 'name' ) )
		propset.setUniqueId( int(xml.attribute( 'id', 0 )) )
		return propset

#--------------------------------------------------------------------------------

class StudiomaxSceneObjectPropSet( StudiomaxScenePropSet ):
	# handle old name conversion
	castModeFgIllumDict = { 'objcolor': 1, 'black': 2, 'invisible': 3 }
	
	def __init__( self, scene, nativePropSet ):
		StudiomaxScenePropSet.__init__( self, scene, nativePropSet )
		
		# define basic properties
		self._defineProperty( 'renderable', 					True )
		self._defineProperty( 'inheritVisibility', 				True )
		self._defineProperty( 'primaryVisibility', 				True )
		self._defineProperty( 'secondaryVisibility', 			True )
		self._defineProperty( 'receiveShadows', 				True )
		self._defineProperty( 'castShadows', 					True )
		self._defineProperty( 'applyAtmospherics', 				True )
		self._defineProperty( 'renderOccluded', 				False )
		self._defineProperty( 'gbufferchannel', 				0 )
		
		# define vray properties
		self._defineProperty( 'VRay_MoBlur_GeomSamples', 		2, 			custom = True )
		self._defineProperty( 'VRay_GI_Generate', 				True, 		custom = True )
		self._defineProperty( 'VRay_GI_Receive', 				True, 		custom = True )
		self._defineProperty( 'VRay_GI_Multipier', 				1, 			custom = True )
		self._defineProperty( 'VRay_GI_GenerateMultipier', 		1, 			custom = True )
		self._defineProperty( 'VRay_Caustics_Generate', 		True, 		custom = True )
		self._defineProperty( 'VRay_Caustics_Receive', 			True, 		custom = True )
		self._defineProperty( 'VRay_Caustics_Multipier', 		1, 			custom = True )
		self._defineProperty( 'VRay_MoBlur_DefaultGeomSamples', True, 		custom = True )
		self._defineProperty( 'VRay_Matte_Enable', 				False, 		custom = True )
		self._defineProperty( 'VRay_Matte_Alpha', 				1, 			custom = True )
		self._defineProperty( 'VRay_Matte_Shadows', 			False, 		custom = True )
		self._defineProperty( 'VRay_Matte_ShadowAlpha', 		False, 		custom = True )
		self._defineProperty( 'VRay_Matte_ShadowBrightness', 	1, 			custom = True )
		self._defineProperty( 'VRay_Matte_ReflectionAmount', 	1, 			custom = True )
		self._defineProperty( 'VRay_Matte_RefractionAmount', 	1, 			custom = True )
		self._defineProperty( 'VRay_Matte_GIAmount', 			1, 			custom = True )
		self._defineProperty( 'VRay_Matte_GI_OtherMattes', 		True, 		custom = True )
		self._defineProperty( 'VRay_Surface_Priority', 			0, 			custom = True )
		self._defineProperty( 'VRay_GI_VisibleToGI', 			True, 		custom = True )
		self._defineProperty( 'VRay_GI_VisibleToReflections',	True,		custom = True )
		self._defineProperty( 'VRay_GI_VisibleToRefractions',	True,		custom = True )

		# define mr properties
		self._defineProperty( 'Mr_castModeFGIllum', 			1 )
		self._defineProperty( 'MR_rcvFGIllum', 					True )
		self._defineProperty( 'GenerateGlobalIllum', 			True )
		self._defineProperty( 'RcvGlobalIllum', 				True )
	
	def _setValueString( self, valueString ):
		"""
			\remarks	sets the value for these properties by the inputed value string, which contains the properties with a '|' separating the values
			\param		valueString		<str>
			\return		<bool> success
		"""
		values = str(valueString).split( '|' )
		for index, key in enumerate(self._keys):
			cval = self._values.get( str(key) )
			try:
				val = values[index]
			except IndexError:
				val = cval
			else:
				if ( type(cval) == bool ):
					val = val == '1' or val == 'True'
				elif val != 'undefined':
					val = eval(val)
			self._values[str(key)] = val
		return True
		
	def _valueString( self ):
		"""
			\remarks	returns the current key/value pairing to a string separated by '|'
			\return		<str>
		"""
		output = []
		for key in self._keys:
			val = self._values.get( str(key), 1 )
			
			# record booleans as integers
			if ( type(val) == bool ):
				val = int(val)
				
			output.append( str(val) )
		
		return '|'.join( output )
		
	def setValue( self, key, value ):
		if ( key == 'Mr_castModeFGIllum' ):
			value = self.castModeFgIllumDict.get( str(value).lower(), value )
		
		return StudiomaxScenePropSet.setValue( self, key, value )
	
	def value( self, key ):
		value = StudiomaxScenePropSet.value( self, key )
		
		# map this property from a name to an integer
		if ( key == 'Mr_castModeFGIllum' ):
			for n, val in self.castModeFgIllumDict.items():
				if ( val == value ):
					return mxs.pyhelper.namify(n)
				
		return value
			
		
# register the class to the system
import cross3d
cross3d.registerSymbol( 'ScenePropSet', 		StudiomaxScenePropSet )
cross3d.registerSymbol( 'SceneObjectPropSet', 	StudiomaxSceneObjectPropSet )
