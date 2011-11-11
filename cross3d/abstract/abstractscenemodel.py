##
#	\namespace	blur3d.api.abstract.abstractscenemodel
#
#	\remarks	The AbstractSceneModel class provides the base foundation for the 3d Object framework for the blur3d system
#				This class will provide a generic overview structure for all manipulations of 3d models
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/05/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneObject

#------------------------------------------------------------------------------------------------------------------------

class AbstractSceneModel( SceneObject ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def displayNameTokens( self ):
		"""
			\remarks	returns the parsed model name as a dictionary. added by douglas.
			\return		<dict> nameTokens
		"""	
		import re
		regex = re.compile(r'^((?P<denomination>[CEVP](-Ly)?)_)?(?P<assetName>[A-Za-z0-9]+)(_|\-)?(?P<iteration>[A-Z]|[0-9\-]+)?$')
		match = regex.match( self.displayName() )
		if match:
			return match.groupdict()
		return {}

	def displayNameMask( self ):
		"""
			\remarks	returns the mask that allows to assemble a model name. added by douglas.
			\return		<str> nameMask
		"""	
		return '%(assetName)s_%(iteration)s'
	
	def displayNameTokenValue( self, token ):
		"""
			\remarks	returns a specified name token. added by douglas.
			\return		<str> tokenValue
		"""	
		if token in self.displayNameTokens():
			return self.displayNameTokens()[ token ]
		return None

	def assetName( self ):
		"""
			\remarks	returns the asset name. added by douglas.
			\return		<str> assetName
		"""	
		return self.displayNameTokenValue( 'assetName' )
	
	def iteration( self ):
		"""
			\remarks	returns the model iteration. added by douglas.
			\return		<str> | <float> iteration
		"""	
		iteration = self.displayNameTokenValue( 'iteration' )
		if iteration:
			iterationReplaced = iteration.replace( '-', '.' )
			try:
				iteration = float( iterationReplaced )
				if int( str( iteration ).split( '.' )[1] ) == 0:
					iteration = int( iteration )
			except:
				pass
		return iteration

	def setIteration( self, iteration, padding=3 ):
		"""
			\remarks	sets the model iteration. added by douglas.
			\return		iteration <str | int | float>
			\return		<bool> success
		"""	
		from blur3d.api import Scene
		scene = Scene()
		try:
			iterationFloat = float( iteration.replace( '-', '.' ) )
			iterationFloatSplit = str( iterationFloat ).split( '.' )
			integer = iterationFloatSplit[0].zfill( padding )
			decimal = iterationFloatSplit[1]
			if int( decimal ) == 0:
				decimal = ''
			iteration = '-'.join( [ integer, decimal ] )
		except:
			pass
		tokens = self.displayNameTokens()
		tokens[ 'iteration' ] = iteration
		newName = self.displayNameMask % tokens
		if scene.isAvalaibleName( newName ):
			self.setDisplayName( newName )
			return True
		return False
		
	def iterationString( self, padding=3, floats=1, floatSeparator='-', floatForce=False ):
		"""
			\remarks	returns a customised string that represent the iteration. does not belong in api. added by douglas.
			\return		<str> iteration
		"""	
		iteration = self.iteration()
		if type( iteration ) is int:
			if floatForce == True:
				iteration = float( iteration )
			else:
				iteration = str( iteration ).zfill( padding )
		if type( iteration ) is float:
			iterationFloatSplit = str( iteration ).split( '.' )
			integer = iterationFloatSplit[0].zfill( padding )
			decimal = iterationFloatSplit[1]
			if len( decimal ) < floats:
				zerosToAdd = floats - len( decimal )
				for i in range( zerosToAdd ):
					decimal = decimal + '0'
			iteration = floatSeparator.join( [ integer, decimal ] )
		return iteration
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
			
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', AbstractSceneModel, ifNotFound = True )