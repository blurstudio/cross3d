##
# 	\namespace	blur3d.api.external
#
#	\remarks	[desc::commented]
#
# 	\author		dougl@blur.com
# 	\author		Blur Studio
# 	\date		01/21/14
#

#------------------------------------------------------------------------------------------------------------------------

from PyQt4.QtCore import QObject

#------------------------------------------------------------------------------------------------------------------------

class External(QObject):

	@classmethod
	def runScript(cls, script, version=None, architecture=64, debug=False):
		return False

	@classmethod
	def binaryBasePath(cls, version=None, architecture=64):
		return False