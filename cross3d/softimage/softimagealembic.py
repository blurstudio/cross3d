##
#   :namespace  blur3d.api.softimage.softimagealembic
#
#   :remarks    [desc::commented]
#   
#   :author     enoch@blur.com
#   :author     Blur Studio
#   :date       07/10/12
#
#------------------------------------------------------------------------------------------------------------------------

from PySoftimage import xsi
from blur3d.api.abstract.abstractalembic import AbstractAlembic

class SoftimageAlembic( AbstractAlembic ):
		
	def _nativeImportFile( self, file ):
		"""
			\remarks	imports alembic file
			\param		
			\return		<bool> success of import
		"""
		# not yet implemented
		return None		
		
	def _nativeExportFile( self, writeJobs ):
		"""
			\remarks	export alembic files contained in writeJobs object
			\param		
			\return		<bool> success of export
		"""
		try:
			xsi.alembic_export( writeJobs.arguments() )
			return True
		except:
			return False
	
	
	def importFile( self ):
		# not yet implemented
		pass
		
	def exportFile( self, writeJobs ):
		success = self._nativeExportFile( writeJobs )
		return success

# register the symbol
from blur3d import api
api.registerSymbol( 'Alembic', SoftimageAlembic )

	

		
		
	
		
		
		
	
		
	