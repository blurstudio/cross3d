##
#	\namespace	blur3d.api.abstract.abstractscenerenderer
#
#	\remarks	The AbstractSceneRenderer class provides an interface to editing renderers in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from abstractscenewrapper import AbstractSceneWrapper

class AbstractSceneRenderer( AbstractSceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	[abstract] allow the user to edit the renderer
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	def rendererType( self ):
		"""
			\remarks	[abstract] return the renderer type for this instance
			\sa			setRendererType
			\return		<blur3d.constants.RendererType>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0
	
	def setRendererType( self, rendererType ):
		"""
			\remarks	[abstract] set the renderer type for this instance to the inputed type
			\sa			rendererType
			\param		rendererType	<blur3d.constants.RendererType>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneRenderer', AbstractSceneRenderer, ifNotFound = True )