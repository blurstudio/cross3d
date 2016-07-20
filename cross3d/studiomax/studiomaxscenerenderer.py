##
#	\namespace	cross3d.abstract.abstractscenerenderer
#
#	\remarks	The StudiomaxSceneRenderer class provides an interface to editing renderers in a Scene environment for a Studiomax application
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 										import mxs
from cross3d.abstract.abstractscenerenderer 		import AbstractSceneRenderer

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
			\return		<cross3d.constants.RendererType>
		"""
		from cross3d.constants import RendererType
		classname = str(mxs.classof(self._nativePointer)).lower()
		
		if ( classname == 'default_scanline_renderer' ):
			return RendererType.Scanline
		elif ( classname == 'mental_ray_renderer' ):
			return RendererType.MentalRay
		elif ( 'v_ray' in classname ):
			return RendererType.VRay
		
		return 0
		
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneRenderer', StudiomaxSceneRenderer )