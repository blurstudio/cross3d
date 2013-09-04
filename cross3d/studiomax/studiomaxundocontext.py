




from PyQt4.QtCore import QObject
from Py3dsMax import mxs

from blur3d.api.abstract.abstractundocontext import AbstractUndoContext
from blur3d import api


class StudiomaxUndoContext(AbstractUndoContext):
	
	def __enter__(self):
		return None
	
	def __exit__(self, exc_type, exc_value, traceback):
		return False
	
	@classmethod
	def openUndo(cls, name):
		pass
	
	@classmethod
	def closeUndo(cls):
		pass
		
	
	
# register the symbol
api.registerSymbol('UndoContext', StudiomaxUndoContext)
	