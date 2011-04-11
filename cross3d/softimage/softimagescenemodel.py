##
#	\namespace	blur3d.api.softimage.softimagesceneobject
#
#	\remarks	The SoftimageSceneObject class provides the implementation of the AbstractSceneObject class as it applies
#				to Softimage
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11
#

from PySoftimage import xsi
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneModel( AbstractSceneModel ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _nativeCamera( self ): # I don't really like that but for now will do
		return self._findNativeChild( 'Camera' )
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def assetType( self ): # not in abstract
		metadata = self.metadata()
		return metadata.attribute( 'assetType' )
		
	def department( self ): # not in abstract. I would call that "stage" but I am matching trax.
		metadata = self.metadata()
		return metadata.attribute( 'department' )

	def displayNameTokens( self ): # not in abstract
		import re
		regex = re.compile(r'^(?P<assetName>[A-Za-z0-9]+)?(_(?P<letterIteration>[A-Z]))$')
		if regex:
			match = regex.match( self.displayName() )
			if match:
				return match.groupdict()
		return None

	def displayNameMask( self ): # not in abstract
		return '%(assetName)s_%(letterIteration)s'
		
	def assetName( self ): # not in abstract
		return self.displayNameTokens()[ 'assetName' ]
	
	def letterIteration( self ): # not in abstract
		return self.displayNameTokens()[ 'letterIteration' ]

	def setLetterIteration( self, letterIteration ): # not in abstract
		tokens = self.displayNameTokens()
		if tokens:
			if tokens[ 'letterIteration' ]: # not in abstract
				from blur3d.api import Scene
				scene = Scene() 
				if scene.isLetterIterationAvailable( letterIteration, tokens[ 'assetName' ] ):
					tokens[ 'letterIteration' ] = letterIteration
					self.setDisplayName( self.displayNameMask % tokens )
					return True
		return True
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', SoftimageSceneModel )

