##
#   :namespace  blur3d.api.maya.external
#
#   :remarks    This class can be used even outside of Maya. It gives you info on where#				Maya is installed, and allows you to run scripts in Maya.
#				To Access this class use: blur3d.api.external('maya')
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       09/10/14
#
import os
from blur3d.api import Exceptions
from blur3d.api.abstract.external import External as AbstractExternal
class External(AbstractExternal):
	_hkeyBase = r'Software\Autodesk\Maya'
	# In case the software is installed but not used don't find it when not passing in a version
	_ignoredVersions = set(os.environ.get('BDEV_STUDIO_IGNORED_MAYA', '').split(','))
	# map years to version numbers. Maya doesnt use these anymore, add older versions if support is needed
	_yearForVersion = {}
	
	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations.
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		def buildHKey(version):
			return r'{hkeyBase}\{version}\Setup\InstallPath'.format(hkeyBase=cls._hkeyBase, version=version)
		version = cls._yearForVersion.get(unicode(version), version)
		hive = 'HKEY_LOCAL_MACHINE'
		valueName = 'MAYA_INSTALL_LOCATION'
		ret = None
		if version == None:
			# Get all of the installed versions so we can find the latest version.
			versions = cls._listRegKeys(hive, cls._hkeyBase, architecture=architecture)
			for v in sorted(versions, reverse=True):
				if v not in cls._ignoredVersions:
					hkey = buildHKey(v)
					try:
						ret = cls._registryValue(hive, hkey, valueName, architecture)[0]
					except WindowsError:
						continue
					if ret:
						version = v
						break
		else:
			hkey = buildHKey(version)
			try:
				ret = cls._registryValue(hive, hkey, valueName, architecture)[0]
			except WindowsError:
				raise Exceptions.SoftwareNotInstalled('Maya', version=version, architecture=architecture, language=language)
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.join(os.path.normpath(ret), 'bin')
		raise Exceptions.SoftwareNotInstalled('Maya', version=version, architecture=architecture, language=language)
				
	@classmethod
	def scriptPath(cls):
		return r'C:\temp\maya_script.py'
		
	@classmethod
	def scriptLog(cls):
		return r'C:\temp\maya_script.log'
