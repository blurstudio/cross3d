/*!
	mxs_pyhelper.ms
	
	this file defines a struct of methods designed to help out the python integration
	for methods that are not easily transferrable to python
*/
global pyhelper
(
	struct PyHelperStruct (
		-- ats ops helper methods
		function getATSFiles = (
			local output = #()
			ATSOps.GetFiles &output
			output
		),
		
		-- layer helper methods
		function getLayerNodes layer		= (
			local output = #()
			layer.nodes &output
			output
		),
		
		-- instance helper methods
		function getInstances object = (
			local output = #()
			instanceMgr.getInstances object &output
			output
		),
		
		-- conversion methods
		function convertValue value type 	= ( value as type ),		-- converts 1 value to another type ( 10 as string ) for instance
		function tobits list				= ( list as bitarray ),		-- convert a list to a bit array
		function namify str 				= ( str as name ),			-- convert a string to a name
		function setCurrentRenderer rend	= ( renderers.current = rend ),
		
		-- clone objects
		function cloneObjects objects = (
			local clones = #()
			maxOps.cloneNodes objects newNodes:&clones
			clones
		),

		-- get subdyn sets from a dynamic master tied to a thinking particle object
		function getSubDyns object = (
			local subdyns = #()
			subdyns = for sub = 1 to object.numsubs collect object[sub]
			subdyns
		),

		-- create selectionsets from current layers
		function layersToSelectionSets = (
			for layerIndex = 1 to ( layerManager.count - 1 ) do (
				local objs 	= #()
				local layer = layerManager.getLayer layerIndex
				layer.nodes &objs
				selectionsets[ layer.name ] = objs
			)
		),

		-- create layers from current selectionsets
		function selectionSetsToLayers					= (
			for setIndex = 1 to selectionSets.count do (
				local layer = layerManager.newLayer()
				layer.setName( getNamedSelSetName setIndex )
				for object in selectionSets[setIndex] do (
					layer.addNode object
				)
			)
		),
		
		function setViewportQuadSize width height = (
			source = "using System;\n"
			source += "using System.Runtime.InteropServices;\n"
			source += "using System.Text;\n"
			source += "class assembly\n"
			source += "{\n"
			source += " [DllImport(\"user32.dll\")]\n"
			source += " public static extern bool SetWindowPos(IntPtr hWnd, int hWndArg, int Left, int Top, int Width, int Height, int hWndFlags);\n"
			source += " [DllImport(\"user32.dll\")]\n"
			source += "	static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);\n"
			source += "	public struct RECT\n"
			source += "	{\n"
			source += "	 public int Left;\n"
			source += "	 public int Top;\n"
			source += "	 public int Right;\n"
			source += "	 public int Bottom;\n"
			source += "	}\n"
			source += "	public int[] getWindowRect(IntPtr hWnd)\n"
			source += "	{\n"
			source += "	 RECT rect;\n"
			source += "	 if ( GetWindowRect(hWnd, out rect) )\n"
			source += "	 {\n"
			source += "	 return new int[] { rect.Left, rect.Top, rect.Right - rect.Left, rect.Bottom - rect.Top };\n"
			source += "	 }\n"
			source += "	 return null;\n"
			source += "	}\n"
			source += "}\n"
			csharpProvider = dotnetobject "Microsoft.CSharp.CSharpCodeProvider"
			compilerParams = dotnetobject "System.CodeDom.Compiler.CompilerParameters"
			compilerParams.GenerateInMemory = on
			compilerResults = csharpProvider.CompileAssemblyFromSource compilerParams #(source)
			assembly = compilerResults.CompiledAssembly.createInstance "assembly"
			compensation = 4
			ViewportHwnd = for w in (windows.getChildrenHWND #max) where w[4] == "ViewPanel" do exit with w[1]
			assembly.setwindowpos (dotNetObject "System.IntPtr" ViewportHwnd) 0 0 0 (width+compensation) (height+compensation) 0x0026
			ForcecompleteRedraw()
		)

	)
	
	pyhelper = PyHelperStruct()
)