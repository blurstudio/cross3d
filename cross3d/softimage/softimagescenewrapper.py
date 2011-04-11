##
#	\namespace	blur3d.api.softimage.softimagescenewrapper
#
#	\remarks	The AbstractSceneWrapper class defines the base class for all other scene wrapper instances.  This creates a basic wrapper
#				class for mapping native object instances from a DCC application to the blur3d structure
#
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11
#

from PySoftimage								import xsi
from blur3d.api.abstract.abstractscenewrapper 	import AbstractSceneWrapper

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneWrapper( AbstractSceneWrapper ):
	pass

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneWrapper', SoftimageSceneWrapper )