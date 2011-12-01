##
#	\namespace	blur3d.scenes
#
#	\remarks	The blur3d.scenes package creates an abstract wrapper from a 3d system
#				to use when dealing with scenes
#				If you need to debug why a software module is failing to load, set _useDebug, and _modName.
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

import blurdev as _blurdev
# If you need to test why a package is failing to import set this to true
_useDebug = _blurdev.debug.debugLevel() == _blurdev.debug.DebugLevel.High
# specify the module you wish to check. This way it will not report the fail to load softimage if you are in max, as this is a expected failure
_modName = _blurdev.core.objectName()

from classes import FrameRange
from classes import Dispatch as _Dispatch
dispatch = _Dispatch()

# initialize the
def init():
	# import any overrides to the abstract symbols
	import glob, os.path, sys
	filenames = glob.glob( os.path.split( __file__ )[0] + '/*/__init__.py' )
	for filename in filenames:
		modname = os.path.normpath( filename ).split( os.path.sep )[-2]
		if ( modname != 'abstract' ):
			pckg = 'blur3d.api.%s' % modname
			
			# try to import the overrides
			if _useDebug and (not _modName or modname == _modName):
				__import__( pckg )
			else:
				try:
					__import__( pckg )
				except ImportError:
					continue
			
			mod = sys.modules[pckg]
			if _useDebug and (not _modName or modname == _modName):
				mod.init()
			else:
				try:
					mod.init()
					break
				except:
					continue
	
	# import the abstract api for default implementations of api
	import abstract
	abstract.init()
	global application
	application = Application()

def registerSymbol( name, value, ifNotFound = False ):
	# initialize a value in the dictionary
	import blur3d.api
	if ( ifNotFound and name in blur3d.api.__dict__ ):
		return
		
	blur3d.api.__dict__[ name ] = value