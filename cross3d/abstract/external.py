##
# 	\namespace	cross3d.external
#
#	\remarks	[desc::commented]
#
# 	\author		dougl
# 	\author		Blur Studio
# 	\date		01/21/14
#

#------------------------------------------------------------------------------------------------------------------------

from PyQt4.QtCore import QObject
from cross3d import abstractmethod
from cross3d.constants import ScriptLanguage

#------------------------------------------------------------------------------------------------------------------------

class External(QObject):
	# map languages to ids
	_languageIDs = {'English': ('409', 'en-US', 'ENU'), 'French': ('40C', 'fr-FR', 'FRA'), 'German': ('407', 'de-DE', 'DEU'), 
					'Japanese': ('411', 'ja-JP', 'JPN'), 'Korean': ('412', 'ko-KR', 'KOR'), 'Simplified Chinese': ('804', 'zh-CN', 'CHS')}

	@classmethod
	@abstractmethod
	def name(cls):
		return ''

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
	def runScript(cls, script, version=None, architecture=64, language=ScriptLanguage.Python, debug=False, headless=True):
		return False
	
	@classmethod
	def scriptPath(cls):
		return r'C:\temp\%s_script.py' % cls.name().lower()
		
	@classmethod
	def scriptLog(cls):
		return r'C:\temp\%s_script.log' % cls.name().lower()