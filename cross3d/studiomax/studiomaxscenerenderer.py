##
#	\namespace	blur3d.api.abstract.abstractscenerenderer
#
#	\remarks	The StudiomaxSceneRenderer class provides an interface to editing renderers in a Scene environment for a Studiomax application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 										import mxs
from blur3d.api.abstract.abstractscenerenderer 		import AbstractSceneRenderer

class StudiomaxSceneRenderer( AbstractSceneRenderer ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	implements AbstractSceneRenderer.edit to allow the user to edit the renderer
			\return		<bool> success
		"""
		medit = mxs.medit
		medit.PutMtlToMtlEditor( self._nativePointer, medit.GetActiveMtlSlot() )
		mxs.matEditor.open()
		return True
	
	def rendererType( self ):
		"""
			\remarks	implements AbstractSceneRenderer.rendererType to return the renderer type for this instance
			\sa			setRendererType
			\return		<blur3d.constants.RendererType>
		"""
		from blur3d.constants import RendererType
		classname = str(mxs.classof(self._nativePointer)).lower()
		
		if ( classname == 'default_scanline_renderer' ):
			return RendererType.Scanline
		elif ( classname == 'mental_ray_renderer' ):
			return RendererType.MentalRay
		elif ( 'v_ray' in classname ):
			return RendererType.VRay
		
		return 0
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneRenderer', StudiomaxSceneRenderer )