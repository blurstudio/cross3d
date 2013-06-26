##
#	\namespace	blur3d.api.softimage.motionbuilderscene
#
#	\remarks	The MotionBuilderScene class will define all the operations for Motion Builder scene interaction.  
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		06/21/12
#

from blur3d.api.abstract.abstractscene import AbstractScene

#------------------------------------------------------------------------------------------------------------------------

class MotionBuilderScene( AbstractScene ):
	def __init__( self ):
		AbstractScene.__init__( self )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'Scene', MotionBuilderScene )