##
#	\namespace	blur3d.api.abstract.abstractscenerenderer
#
#	\remarks	The AbstractSceneRenderer class provides an interface to editing renderers in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d import abstractmethod
from blur3d.api import SceneWrapper
from blur3d import api


class AbstractSceneRenderer(SceneWrapper):
	"""
	The SceneRenderer class provides an interface to editing 
	renderers in a Scene environment for any DCC application
	"""
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def edit(self):
		"""
		Allow the user to edit the renderer

		"""
		return False

	@abstractmethod
	def rendererType(self):
		"""
		Return the renderer type for this instance
		
		:return: :data:`blur3d.constants.RendererType`
		
		"""
		return 0

	@abstractmethod
	def setRendererType(self, rendererType):
		"""
		Set the renderer type for this instance to the inputed type
		
		:param rendererType: :data:`blur3d.constants.RendererType`
		:return: bool

		"""
		return False


# register the symbol
api.registerSymbol('SceneRenderer', AbstractSceneRenderer, ifNotFound=True)
