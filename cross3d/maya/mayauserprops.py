from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps, AbstractFileProps

class MayaUserProps(AbstractUserProps):
	pass

class MayaFileProps(MayaUserProps):
	pass

# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', MayaUserProps )
api.registerSymbol( 'FileProps', MayaFileProps )