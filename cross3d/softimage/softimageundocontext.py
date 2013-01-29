




from PyQt4.QtCore import QObject
from PySoftimage import xsi

from blur3d.api.abstract.abstractundocontext import AbstractUndoContext
from blur3d import api


class SoftimageUndoContext(AbstractUndoContext):
	
	def __enter__(self):
		xsi.OpenUndo(self.name)
		return None
	
	def __exit__(self, exc_type, exc_value, traceback):
		xsi.CloseUndo()
		return False
	
	@classmethod
	def openUndo(cls, name):
		xsi.OpenUndo(name)
	
	@classmethod
	def closeUndo(cls):
		xsi.CloseUndo()
		
	
	
# register the symbol
api.registerSymbol('UndoContext', SoftimageUndoContext)
	