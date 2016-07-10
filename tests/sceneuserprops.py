import pytest
import cross3d

@pytest.fixture
def SceneObjectUserProps():
	scene = cross3d.Scene()
	# TODO: This is probably not the best way to get a object to test userProps on
	obj = scene.selection()[0]
	obj.userProps().clear()
	data = {
		'integer' : 125,
		'ffloat' : 147.56,
		'llist' : [1,2,3],
		'ddict' : {"Test":"item", "tInt": 10, "tfloat": 12.45},
		'ttuple' : (123, 498),
		'tboolean': True,
		'fboolean': False
	}
	# Store info from the data dict in userProps
	for key, value in data.items():
		obj.userProps()[key] = value

	for key in data:
		assert data[key] == obj.userProps()[key], "UserProp value not equal. Original: {orig} UserProp: {prop}".format(orig=data[key], prop=obj.userProps()[key])