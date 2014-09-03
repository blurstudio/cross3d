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
from blur3d import abstractmethod

#------------------------------------------------------------------------------------------------------------------------

class External(QObject):

	@classmethod
	@abstractmethod
	def getFileVersion(cls, filepath):
		""" Reads the version info that was saved to a custom dso property
		added to the file when saved from its application.
		"""
		return None

	@classmethod
	@abstractmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		return False
	
	@classmethod
	@abstractmethod
	def runScript(cls, script, version=None, architecture=64):
		return False
	
	@classmethod
	@abstractmethod
	def scriptPath(cls):
		return r'C:\temp\abstract_script.py'

	@classmethod
	@abstractmethod
	def scriptLog(cls):
		return r'C:\temp\abstract_script.log'
	
	@classmethod
	def _registryValue(cls, registry, key, value, architecture=64):
		# Do not want to import _winreg unless it is neccissary
		import _winreg
		aReg = _winreg.ConnectRegistry(None, getattr(_winreg, registry))
		if architecture == 32:
			sam = _winreg.KEY_WOW64_32KEY
		else:
			sam = _winreg.KEY_WOW64_64KEY
		try:
			regKey = _winreg.OpenKey(aReg, key, 0, _winreg.KEY_READ | sam)
			return _winreg.QueryValueEx(regKey, value)
		except WindowsError:
			pass
		return ('', 0)
