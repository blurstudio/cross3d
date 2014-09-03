##
#   :namespace  blur3d.api.studiomax.external
#
#   :remarks    This class can be used even outside of studiomax. It gives you info on where
#				studiomax is installed, and allows you to run scripts in studiomax.
#				To Access this class use: blur3d.api.external('studiomax')
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       09/03/14
#

import os
import subprocess

from blur3d.api.abstract.external import External as AbstractExternal
from blurdev.media import dsofile

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):

	_architectureTokens = {64: r'_x64', 32: r''}
	_versionTokens = {2012: r'Max2012'}

	@classmethod
	def getFileVersion(cls, filepath):
		"""
		Reads the max version that a max file was saved with from a custom 
		dso property added to the file when it is saved from max.
		"""
		dso = dsofile.DSOFile()
		try:
			dso.open(filepath)
			saved_as_version = dso.customProperty('SavedAsVersion')
			if saved_as_version:
				return saved_as_version.value()
		except:
			raise
		return None
	
	@classmethod
	def runScript(cls, script, version=None, architecture=64):

		if os.path.exists(script):
			scriptPath = script

		else:
			scriptPath = cls.scriptPath()
			fle = open(scriptPath, "w")
			fle.write(script)
			fle.close()

		binary = os.path.join(cls.binariesPath(version, architecture), '3dsmax.exe')
		process = subprocess.Popen([binary, '-U', 'MAXScript', scriptPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		
		# Writing the log file.
		fle = open(cls.scriptLog(), 'w')
		fle.write(process.stdout.read())
		fle.close()

		# Checking the error in the log file.
		fle = open(cls.scriptLog())
		content = fle.read()

		return False if 'FATAL' in content else True

	@classmethod
	def scriptPath(cls):
		return r'C:\temp\studiomax_script.py'

	@classmethod
	def scriptLog(cls):
		return r'C:\temp\studiomax_script.log'

	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations. Does not need to be
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		# map years to version numbers
		versionForYear = {'2008': '10.0', '2009': '11.0', '2010': '12.0', '2011': '13.0', '2012': '14.0', 
							'2013': '15.0', '2014': '16.0', '2015': '17.0'}
		# map languages to ids
		languageIDs = {'English': ('409', 'en-US', 'ENU'), 'French': ('40C', 'fr-FR', 'FRA'), 'German': ('407', 'de-DE', 'DEU'), 
						'Japanese': ('411', 'ja-JP', 'JPN'), 'Korean': ('412', 'ko-KR', 'KOR'), 'Simplified Chinese': ('804', 'zh-CN', 'CHS')}
		try:
			version = versionForYear[unicode(version)]
		except KeyError:
			raise Exception('Invalid version or architecture.')
		langId = languageIDs.get(language, languageIDs['English'])
		# Ensure we get a valid version number
		version = '{}.0'.format(version[:version.find('.')])
		if float(version) >= 15:
			ret = cls._registryValue('HKEY_LOCAL_MACHINE', r'Software\Autodesk\3dsMax\{version}'.format(version=version), 'Installdir', architecture)[0]
		else:
			ret = cls._registryValue('HKEY_LOCAL_MACHINE', r'Software\Autodesk\3dsMax\{version}\MAX-1:{langId}'.format(version=version, langId=langId[0]), 'Installdir', architecture)[0]
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.normpath(ret)
		return False
