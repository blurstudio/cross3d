##
#   \namespace  blur3d.io.softimagewritejobs
#
#   \remarks    [desc::commented]
#   
#   \author     enoch@blur.com
#   \author     Blur Studio
#   \date       05/10/12
#


class AbstractWriteJobs( list ):
	def add( self, job ):
		self.append( job )
	
class SoftimageWriteJobs( AbstractWriteJobs ):
	def arguments( self ):
		return '|'.join( job.arguments() for job in self )
		
		
