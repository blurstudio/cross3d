##
#	\namespace	blur3d.api.abstract.abstractscenerenderer
#
#	\remarks	The AbstractSceneRenderer class provides an interface to editing renderers in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper

class AbstractSceneRenderer( SceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def edit( self ):
		"""
			\remarks	allow the user to edit the renderer
			\return		<bool> success
		"""
		return False
	
	@abstractmethod	
	def rendererType( self ):
		"""
			\remarks	return the renderer type for this instance
			\sa			setRendererType
			\return		<blur3d.constants.RendererType>
		"""
		return 0
	
	@abstractmethod
	def setRendererType( self, rendererType ):
		"""
			\remarks	set the renderer type for this instance to the inputed type
			\sa			rendererType
			\param		rendererType	<blur3d.constants.RendererType>
			\return		<bool> success
		"""
		return False
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneRenderer', AbstractSceneRenderer, ifNotFound = True )