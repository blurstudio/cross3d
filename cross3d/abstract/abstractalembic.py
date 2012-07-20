##
#   :namespace  blur3d.api.abstract.abstractalembic
#
#   :remarks    [desc::commented]
#   
#   :author     enoch@blur.com
#   :author     Blur Studio
#   :date       07/10/12
#

from blur3d import abstractmethod

class AbstractAlembic:
	
	@abstractmethod
	def _nativeImportFile( self, file ):
		"""
			\remarks	imports alembic file
			\param		
			\return		<bool> success of import
		"""
		return None		
		
	@abstractmethod
	def _nativeExportFile( self, writeJobs ):
		"""
			\remarks	export alembic files contained in writeJobs object
			\param		
			\return		<bool> success of export
		"""
		return None		
	
	def importFile( self ):
		# not yet implemented
		pass
		
	def exportFile( self, writeJobs ):
		success = self._nativeExportFile( writeJobs )
		return success

# register the symbol
from blur3d import api
api.registerSymbol( 'Alembic', AbstractAlembic, ifNotFound = True )