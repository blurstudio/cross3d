/*!
	helpers.ms

	this file defines a struct of methods designed to help out the python integration
	for methods that are not easily transferrable to python
*/
_blurLibrary.load "blurPointCache"

global blur3dhelper
(
	struct Blur3dHelperStruct (

		function buildLightMeterBox position width:100 length:100 wSegs:3 lSegs:3 = (
			lm1 = VRayLightMeter()
			lm2 = VRayLightMeter()
			lm3 = VRayLightMeter()
			lm4 = VRayLightMeter()
			lm5 = VRayLightMeter()
			lm6 = VRayLightMeter()
			lm2.rotation = (eulerAngles 0 90 0)
			lm3.rotation = (eulerAngles 90 0 90)
			lm5.rotation = (eulerAngles 0 -90 0)
			lm6.rotation = (eulerAngles -90 0 -90)
			lms = #(lm1, lm2, lm3, lm4, lm5, lm6)
			for lm in lms do (
				lm.pos = position
				lm.width = width
				lm.length = length
				lm.wSegs = wSegs
				lm.lSegs = lSegs
			)
			lms
		),

		function getAverageLightEnergyAtPosition position = (
			meters = buildLightMeterBox position
			averages = #()
			for meter in meters do (
				meter.calculate()
				mAvg = for energy in meter.total where energy > 0 collect energy
				ttl = 0
				for avg in mAvg do (
					ttl = (avg + ttl)
				)
				append averages (ttl / mAvg.count)
			)
			delete meters
			ttl = 0
			for avg in averages do (
				ttl = (ttl + avg)
			)
			ttl / averages.count
		),

		function getMeshElements obj = (
			elements = #()
			prev = #()
			for fid = 1 to obj.numFaces do (
				element = ((meshop.getElementsUsingFace obj fid) as array)
				if element.count == prev.count do (
					if (for i = 1 to element.count where element[i] != prev[i] collect i).count == 0 do (
						prev = element
						continue
					)
				)
				append elements element
				prev = element
			)
			elements
		),

		function getSelectedVertPositions = (
			vs = ((getVertSelection $) as array)
			vertPositions = #()
			for vid in vs do (
				append vertPositions (getVert $ vid)
			)
			vertPositions
		),

		function removeAllRetimers = (
			t = trackviewnodes
			n = t[#Retimer_Manager]
			if n != undefined do (
				deleteTrackViewController t n.controller
				gc()
			)
		),

		function removeMotionClipTracks = (
			mcm = trackViewNodes[#Max_MotionClip_Manager]
			if mcm != undefined do (
				mcm.track = copy trackViewNodes[#Max_MotionClip_Manager].track
				gc()
			)
		),

		function setModifyMode = (
			max modify mode
		),

		function getScreenSpaceBoundingBoxes nodes = (
			currentSelection = (selection as array)
			view = viewport.activeViewport
			gw.setTransform (matrix3 1)
			transPoint = gw.hTransPoint
			local bmin = [1e9,1e9,0], bmax = [-1e9,-1e9,0]
			for node in nodes do (
				if (superClassOf node) == GeometryClass do (
					select node
					mesh = snapshotasmesh node
					for v=1 to mesh.numverts do
					(
						vp = transPoint (GetVert mesh v)
						if vp == undefined do continue
						if vp.x < bmin.x do bmin.x = vp.x
						if vp.x > bmax.x do bmax.x = vp.x
						if vp.y < bmin.y do bmin.y = vp.y
						if vp.y > bmax.y do bmax.y = vp.y
					)
					free mesh
				)
			)
			pMin = point2 ((bmin.x as float) / (gw.getWinSizeX() as float)) ((bmin.y as float) / (gw.getWinSizeY() as float))
			pMax = point2 ((bmax.x as float) / (gw.getWinSizeX() as float)) ((bmax.y as float) / (gw.getWinSizeY() as float))
			bbox = #(pMin, pMax)
			select currentSelection
			bbox
		),

		function turntableHelperBuilder cam startFrame endFrame = (
			helper = (dummy name:"TurntableHelper")
			numFrames = (endFrame - startFrame)
			mult = ((360.0 / numFrames) as string)
			fStart = (startFrame as string)
			fEnd = (endFrame as string)
			expr = "degToRad (" + mult + " * (F - " + fStart + "))"
			helper.rotation.z_rotation.controller = Float_Script()
			helper.rotation.z_rotation.controller.script = expr
			helper
		),

		function selectObjectsByNameFilter obj = ( obj.layer == (globalVars.get #FILTERLAYER) ),

		function selectObjectsByNameFromLayer layer = (
			global FILTERLAYER = layer
			local userObjs = selectByName title:"Select Objects" buttonText:"Select" filter:( selectObjectsByNameFilter )
			if ( userObjs != undefined ) then select userObjs
		),

		function appendToMultiMtl mtl = (
			current = mtl.materialList.count
			mtl.materialList.count = (current + 1)
			mtl.mapEnabled[(current + 1)] = on
			mtl.materialIDList[(current + 1)] = (current + 1)
			mtl.names[(current + 1)] = ""
		),

		function removeBitmapSubs bitmap = (
			tvps = getclassinstances bitmaptex asTrackViewPick:true
			for tvp in tvps do (
				if tvp.client[tvp.subNum].value == bitmap do (
					tvp.client[tvp.subNum].value = undefined
				)
			)
		),

		-- Visibility toggle for PC objects.
		function togglePointCaches mods state = (
			pcMods = #()
			for i = 1 to mods.count do
				if classOf mods[i] == Point_Cache do
					append PCMods mods[i]
			for i = 1 to pcMods.count do (
				if state != pcMods[i].enabled do (
					if ( not state and _blurPointCache.canDisablePCObject obj ) then
						pcMods[i].enabled = false
					else
						pcMods[i].enabled = true
				)
			)
		),

		function hasVisibleDescendent obj = (
			local found = false
			if ( obj != undefined ) do (
				if ( not obj.isHidden ) then (
					found = true
				)
				else (
					for child in obj.children do (
						if ( blur3dhelper.hasVisibleDescendent child ) do (
							found = true
							exit
						)
					)
				)
			)
			found
		),

		function hasVisibleReference obj = (
			local found = false
			if ( obj != undefined ) do (
				if ( not obj.isHidden ) then (
					found = true
				)
				else (
					for obj in refs.dependentNodes obj do (
						if ( blur3dhelper.hasVisibleReference obj ) then (
							found = true
							exit
						)
					)
				)
			)
			found
		),

		function canDisableTMController ctrl = (
			local objs = refs.dependentNodes ctrl
			local success = true
			for obj in objs do (
				if ( isValidNode obj ) do (
					if ( not obj.isHidden or classOf obj == hairFxView ) do (
						success = false
						exit
					)
					if ( blur3dhelper.hasVisibleDescendent obj ) do (
						success = false
						exit
					)
					if ( blur3dhelper.hasVisibleReference obj ) do (
						success = false
						exit
					)
				)
			)
			success
		),

		function toggleSubDyn subDyn state = (
			subDyn.on = state
		),

		function toggleTransformCache obj state = (
			if ( isproperty obj #controller and classof obj.controller == transform_cache ) do (
				if ( obj.controller.enabled != state ) do (
					if ( not state and blur3dhelper.canDisableTMController obj.controller ) then (
						obj.controller.enabled = false
					)
					else (
						obj.controller.enabled = true
					)
				)
			)
		),

		function getPositionController object axis:undefined = (
			axisOrder = #("x", "y", "z")
			controller = object.pos.controller
			XYZControllers = getXYZControllers controller
			if axis != undefined then (
				aIndex = findItem axisOrder axis
				if aIndex == 0 then (
					return controller
				)
				return XYZControllers[aIndex]
			)
			return controller
		),

		function setPositionController object controller = (
			object.pos.controller = controller
		),

		function getRotationController object axis:undefined = (
			axisOrder = #("x", "y", "z")
			controller = object.rotation.controller
			XYZControllers = getXYZControllers controller
			if axis != undefined then (
				aIndex = findItem axisOrder axis
				if aIndex == 0 then(
					return controller
				)
				return XYZControllers[aIndex]
			)
			return controller
		),

		function setRotationController object controller = (
			object.rotation.controller = controller
		),

		function getScaleController object = (
			return object.scale.controller
		),

		function setScaleController object controller = (
			object.scale.controller = controller
		),

		function getTransformController object = (
			return object.transform.controller
		),

		function setTransformController object controller = (
			object.transform.controller = controller
		),

		function replaceTransformController source target frame swapHandedness:false = (
			at time frame (
				if swapHandedness then (
					mm = source.transform
					pc = pymax.import "blur3d.lib.cartesian"
					pm = pc.Matrix4x4.newFromMaxMatrix mm
					spm = pm.swapHandedness()
					smm = spm.newMaxMatrix()
					with animate on target.transform = smm
				)
				else (
					with animate on target.transform = source.transform
				)
			)
		),

		function replaceCameraProperties source target frame = (
			targetClass = classof target
			sourceClass = classof source
			at time frame (
				with animate on (
					if targetClass == freecamera and sourceClass != VRayPhysicalCamera do (
						target.fov = source.fov
						target.nearclip = source.nearclip
						target.farclip = source.farclip
					)
					if sourceClass == VRayPhysicalCamera and targetClass == freecamera do (
						target.mpassEffect.focalDepth = source.focus_distance
						if source.specify_fov == on then (
							target.fov = source.fov
						)
						else (
							-- If the fov is not specified specifically then we have
							-- to compute it from the focal length and film gate width.
							target.fov = ((atan (source.film_width / 2.0 / source.focal_length)) * 2.0)
						)
					)
				)
			)
		),

		function objectIsAnimated object = (
			object.transform.isAnimated
		),

		function getFirstPositionKeyFrameNumber object = (
			if object.position.isAnimated do (
				try (
					return object.position.controller.keys[1].time.frame
				)
				catch()
			)
		),

		function getElementUsingFace obj faceID = (
			try (
				return (meshop.getElementsUsingFace obj #(faceID))
			)
			catch ()
		),

		function getVertsUsingFace obj faceList = (
			try (
				return (meshop.getVertsUsingFace obj faceList)
			)
			catch ()
		),

		function asArray thing = (
			try (
				return (thing as array)
			)
			catch ()
		),

		function asBitArray thing = (
			try (
				return (thing as bitArray)
			)
			catch ()
		),

		function asName thing = (
			try (
				return (thing as name)
			)
			catch()
		),

		function setMorpherChannelValue m c v = (
			try (
				WM3_MC_SetValue m c (v as float)
			)
			catch()
		),

		function setAnimate v = (
			if v then (
				set animate on
			)
			else (
				set animate off
			)
		),

		function layerNodes l = (
			l.nodes &theNodes
			return theNodes
		),

		function getLastPositionKeyFrameNumber object = (
			if object.position.isAnimated do (
				try (
					return object.position.controller.keys[object.position.controller.keys.count].time.frame
				)
				catch()
			)
		),

		-- get subdyn sets from a dynamic master tied to a thinking particle object
		function getSubDyns object = (
			local subdyns = #()
			subdyns = for sub = 1 to object.numsubs collect object[sub]
			subdyns
		),

		function setCommandPanelToMod = (
			setCommandPanelTaskMode #modify
		),

		function setKeyAtTime controller value curTime = (
			with animate on (
				key = addNewKey controller curTime
				key.value = value
			)
		),
		function cloneObjects objects expandHierarchy:false cloneType:#copy = (
			local clones = #()
			maxOps.cloneNodes objects newNodes:&clones expandHierarchy:expandHierarchy cloneType:cloneType
			clones
		),
		function maxQuickRender = (
			max quick render
		)
	)

	blur3dhelper = Blur3dHelperStruct()
)
