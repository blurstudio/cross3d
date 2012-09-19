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
from blur3d import api


class AbstractAlembic:

	@abstractmethod
	def _nativeImportFile(self, filepath):
		"""Imports alembic file.
		
		:return: success of import
		:rtype: bool

		"""
		return None

	@abstractmethod
	def _nativeExportFile(self, writeJobs):
		"""Export alembic files contained in writeJobs object
		
		:return: success of export
		:rtype: bool

		"""
		return None

	def importFile(self, filepath):
		"""Imports alembic file.
		
		:return: success of import
		:rtype: bool

		"""
		success = self._nativeImportFile(filepath)
		return success

	def exportFile(self, writeJobs):
		"""Export alembic files contained in writeJobs object
		
		:return: success of export
		:rtype: bool

		"""
		success = self._nativeExportFile(writeJobs)
		return success


# register the symbol
api.registerSymbol('Alembic', AbstractAlembic, ifNotFound=True)
