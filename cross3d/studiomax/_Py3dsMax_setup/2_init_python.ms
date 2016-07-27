-- Check if the Python DLL is installed
if ( pymax != undefined ) then (
	-- Starting with Max 2015 we need to initialize Autodesk's python before our python is initialized
	if (python != undefined) and (finditem (getPropNames python) #exec == 0) do
		python.init()
	-- pymax did not have a init method in the past.
	if (finditem (getPropNames pymax) #init != 0) do
		pymax.init()
	-- Add default python path to sys.path
	pymax.import "py3dsMax_startup"
)
