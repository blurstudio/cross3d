##
#   \namespace  blur3d.io.alembic
#
#   \remarks    [desc::commented]
#   
#   \author     enoch@blur.com
#   \author     Blur Studio
#   \date       00/00/0000
#

#------------------------------------------------------------------------------------------------------------------------

import os

class SoftimageAlembic:
	def importFile():
		pass
		
	def exportFile( self, writeJobs ):
		from PySoftimage import xsi
		xsi.alembic_export( writeJobs.arguments() )
		
	
	


		

		

		
		
	
		
		
		
	
		
	