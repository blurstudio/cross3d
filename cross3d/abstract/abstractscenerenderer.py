##
#	\namespace	cross3d.abstract.abstractscenerenderer
#
#	\remarks	The AbstractSceneRenderer class provides an interface to editing renderers in a Scene environment for any DCC application
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import cross3d
from cross3d import SceneWrapper, abstractmethod


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
		
		:return: :data:`cross3d.constants.RendererType`
		
		"""
		return 0

	@abstractmethod
	def setRendererType(self, rendererType):
		"""
		Set the renderer type for this instance to the inputed type
		
		:param rendererType: :data:`cross3d.constants.RendererType`
		:return: bool

		"""
		return False


# register the symbol
cross3d.registerSymbol('SceneRenderer', AbstractSceneRenderer, ifNotFound=True)
