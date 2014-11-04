##
#   :namespace  blur3d.api.maya.mayaexceptionrouter
#
#   :remarks    Context that converts native exceptions in maya to Blur3d exceptions.
#				This Context is used to capture common exceptions raised in the Software. It 
#				identifies the exception and raises a Blur3d.api.Exceptions exception instead. If it
#				can not identify the exception, it raises the existing exception.
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       11/04/14
#
from blur3d.api import Exceptions
from blur3d import api

class MayaExceptionRouter(object):
	""" This Context is used to capture common exceptions raised in the Software. It identifies the
	exception and raises a Blur3d.api.Exceptions exception instead. If it can not identify the
	exception, it raises the existing exception.
	"""
	def __enter__(self):
		pass
	
	def __exit__(self, exec_type, exec_value, traceback):
		if hasattr(exec_value, 'message'):
			if exec_value.message == '(kInvalidParameter): Argument is a NULL pointer':
				# This exception is raised when you try to access a MObject via MObjectHandle that
				# no longer exists in the scene.
				raise Exceptions.InvalidNativeObject('The Native Pointer is invalid')
		# re-raise the exception
		return False

# register the symbol
api.registerSymbol('ExceptionRouter', MayaExceptionRouter)