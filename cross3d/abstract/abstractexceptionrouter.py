##
#   :namespace  cross3d.abstract.abstractexceptionrouter
#
#   :remarks    Abstract context that converts native exceptions to Blur3d exceptions.
#				This Context is used to capture common exceptions raised in the Software. It 
#				identifies the exception and raises a cross3d.Exceptions exception instead. If it
#				can not identify the exception, it raises the existing exception.
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       11/04/14
#

import cross3d

class AbstractExceptionRouter(object):
	""" This Context is used to capture common exceptions raised in the Software. It identifies the
	exception and raises a cross3d.Exceptions exception instead. If it can not identify the
	exception, it raises the existing exception.
	"""
	def __enter__(self):
		pass
	
	def __exit__(self, exec_type, exec_value, traceback):
		# re-raise the exception
		return False

# register the symbol
cross3d.registerSymbol('ExceptionRouter', AbstractExceptionRouter, ifNotFound=True)
