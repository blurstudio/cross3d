##
#   \namespace  blur3d.io.softimagewritejobs
#
#   \remarks    [desc::commented]
#   
#   \author     enoch@blur.com
#   \author     Blur Studio
#   \date       05/10/12
#


from blur3d.api.abstract.abstractwritejobs import AbstractWriteJobs
	
class SoftimageWriteJobs( AbstractWriteJobs ):
	def arguments( self ):
		return '|'.join( job.arguments() for job in self )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'WriteJobs', SoftimageWriteJobs )
		
		
