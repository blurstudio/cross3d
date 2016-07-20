#--------------------------------------------------------------------------------
#								Read registy values
#--------------------------------------------------------------------------------
def getRegKey(registry, key, architecture=None):
	""" Returns a _winreg hkey or none.
	
	Args:
		registry (str): The registry to look in. 'HKEY_LOCAL_MACHINE' for example
		key (str): The key to open. r'Software\Autodesk\Softimage\InstallPaths' for example
		architecture (int | None): 32 or 64 bit. If None use system default. Defaults to None
	
	Returns:
		A _winreg handle object
	"""
	# Do not want to import _winreg unless it is neccissary
	regKey = None
	import _winreg
	aReg = _winreg.ConnectRegistry(None, getattr(_winreg, registry))
	if architecture == 32:
		sam = _winreg.KEY_WOW64_32KEY
	elif architecture == 64:
		sam = _winreg.KEY_WOW64_64KEY
	else:
		sam = 0
	try:
		regKey = _winreg.OpenKey(aReg, key, 0, _winreg.KEY_READ | sam)
	except WindowsError:
		pass
	return regKey

def listRegKeyValues(registry, key, architecture=None):
	""" Returns a list of child keys and their values as tuples.
	
	Each tuple contains 3 items.
		- A string that identifies the value name
		- An object that holds the value data, and whose type depends on the underlying registry type
		- An integer that identifies the type of the value data (see table in docs for _winreg.SetValueEx)
	
	Args:
		registry (str): The registry to look in. 'HKEY_LOCAL_MACHINE' for example
		key (str): The key to open. r'Software\Autodesk\Softimage\InstallPaths' for example
		architecture (int | None): 32 or 64 bit. If None use system default. Defaults to None
	
	Returns:
		List of tuples
	"""
	import _winreg
	regKey = getRegKey(registry, key, architecture=architecture)
	ret = []
	if regKey:
		subKeys, valueCount, modified = _winreg.QueryInfoKey(regKey)
		for index in range(valueCount):
			ret.append(_winreg.EnumValue(regKey, index))
	return ret

def listRegKeys(registry, key, architecture=None):
	import _winreg
	regKey = getRegKey(registry, key, architecture=architecture)
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

def registryValue(registry, key, value_name, architecture=None):
	""" Returns the value and type of the provided registry key's value name.
	
	Args:
		registry (str): The registry to look in. 'HKEY_LOCAL_MACHINE' for example
		key (str): The key to open. r'Software\Autodesk\Softimage\InstallPaths' for example
		value_name (str): The name of the value to read. To read the '(Default)' key pass a 
			empty string.
		architecture (int | None): 32 or 64 bit. If None use system default. Defaults to None
	
	Returns:
		object: Value stored in key
		int: registry type for value. See _winreg's Value Types
	"""
	# Do not want to import _winreg unless it is neccissary
	regKey = getRegKey(registry, key, architecture=architecture)
	if regKey:
		import _winreg
		return _winreg.QueryValueEx(regKey, value_name)
	return '', 0
