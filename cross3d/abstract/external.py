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
from blur3d.constants import ScriptLanguage

#------------------------------------------------------------------------------------------------------------------------

class External(QObject):
	# map languages to ids
	_languageIDs = {'English': ('409', 'en-US', 'ENU'), 'French': ('40C', 'fr-FR', 'FRA'), 'German': ('407', 'de-DE', 'DEU'), 
					'Japanese': ('411', 'ja-JP', 'JPN'), 'Korean': ('412', 'ko-KR', 'KOR'), 'Simplified Chinese': ('804', 'zh-CN', 'CHS')}

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
	def runScript(cls, script, version=None, architecture=64, language=ScriptLanguage.Python, debug=False):
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
	def _getRegKey(cls, registry, key, architecture=64):
		""" Returns a _winreg hkey or none.
		:param registry: The registry to look in. 'HKEY_LOCAL_MACHINE' for example
		:param key: The key to open. r'Software\Autodesk\Softimage\InstallPaths' for example
		:param architecture: 32 or 64 bit. Defaults to 64bit
		:return: A _winreg handle object
		"""
		# Do not want to import _winreg unless it is neccissary
		regKey = None
		import _winreg
		aReg = _winreg.ConnectRegistry(None, getattr(_winreg, registry))
		if architecture == 32:
			sam = _winreg.KEY_WOW64_32KEY
		else:
			sam = _winreg.KEY_WOW64_64KEY
		try:
			regKey = _winreg.OpenKey(aReg, key, 0, _winreg.KEY_READ | sam)
		except WindowsError:
			pass
		return regKey
	
	@classmethod
	def _listRegKeyValues(cls, registry, key, architecture=64):
		""" Returns a list of child keys and their values as tuples.
		Each tuple contains 3 items.
			- A string that identifies the value name
			- An object that holds the value data, and whose type depends on the underlying registry type
			- An integer that identifies the type of the value data (see table in docs for _winreg.SetValueEx)
		:param registry: The registry to look in. 'HKEY_LOCAL_MACHINE' for example
		:param key: The key to open. r'Software\Autodesk\Softimage\InstallPaths' for example
		:param architecture: 32 or 64 bit. Defaults to 64bit
		:return: List of tuples
		"""
		import _winreg
		regKey = cls._getRegKey(registry, key, architecture=architecture)
		ret = []
		if regKey:
			subKeys, valueCount, modified = _winreg.QueryInfoKey(regKey)
			for index in range(valueCount):
				ret.append(_winreg.EnumValue(regKey, index))
		return ret
	
	@classmethod
	def _listRegKeys(cls, registry, key, architecture=64):
		import _winreg
		regKey = cls._getRegKey(registry, key, architecture=architecture)
		ret = []
		if regKey:
			index = 0
			while True:
				try:
					ret.append(_winreg.EnumKey(regKey, index))
					index += 1
				except WindowsError:
					break
		return ret
	
	@classmethod
	def _registryValue(cls, registry, key, value_name, architecture=64):
		""" Returns the value of the provided registry key's value name.
		:param registry: The registry to look in. 'HKEY_LOCAL_MACHINE' for example
		:param key: The key to open. r'Software\Autodesk\Softimage\InstallPaths' for example
		:param architecture: 32 or 64 bit. Defaults to 64bit
		:return: Value of the registry
		"""
		# Do not want to import _winreg unless it is neccissary
		regKey = cls._getRegKey(registry, key, architecture=architecture)
		if regKey:
			import _winreg
			return _winreg.QueryValueEx(regKey, value_name)
		return ('', 0)
