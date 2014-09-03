##
#   :namespace  blur3d.api.motionbuilder.external
#
#   :remarks    This class can be used even outside of motionbuilder. It gives you info on where
#				motionbuilder is installed, and allows you to run scripts in motionbuilder.
#				To Access this class use: blur3d.api.external('motionbuilder')
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       09/03/14
#

#------------------------------------------------------------------------------------------------------------------------

import os

from blur3d.api.abstract.external import External as AbstractExternal

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):
	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations. Does not need to be
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		ret = cls._registryValue('HKEY_LOCAL_MACHINE', r'Software\Autodesk\MotionBuilder\{version}'.format(version=version), 'InstallPath', architecture)[0]
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.normpath(ret)
		return False

	@classmethod
	def scriptPath(cls):
		return r'C:\temp\motionbuilder_script.py'

	@classmethod
	def scriptLog(cls):
		return r'C:\temp\motionbuilder_script.log'