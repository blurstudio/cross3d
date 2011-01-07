##
#	\namespace	blur3d.scenes
#
#	\remarks	The blur3d.scenes package creates an abstract wrapper from a 3d system
#				to use when dealing with scenes
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

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
			try:
				__import__( pckg )
			except:
				continue
			
			mod = sys.modules[pckg]
			try:
				mod.init()
				break
			except:
				continue
	
	# import the abstract api for default implementations of api
	import abstract
	abstract.init()

def registerSymbol( name, value, ifNotFound = False ):
	# initialize a value in the dictionary
	import blur3d.api
	if ( ifNotFound and name in blur3d.api.__dict__ ):
		return
		
	blur3d.api.__dict__[ name ] = value
	