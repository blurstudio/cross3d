
import cross3d
from cross3d.abstract.abstractundocontext import AbstractUndoContext


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
cross3d.registerSymbol('UndoContext', StudiomaxUndoContext)
