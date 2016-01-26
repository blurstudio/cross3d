##
#	\namespace	blur3d.api.studiomax.studiomaxscenecamera
#
#	\remarks	The StudiomaxSceneCamera class provides the implementation of the AbstractSceneCamera class as it applies
#				to 3d Studio Max scenes
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

import os
import random
import blur3d.api

from Py3dsMax import mxs
from PyQt4.QtGui import QColor
from PyQt4.QtCore import QSize
from blur3d.api import application
from blur3d import pendingdeprecation
from blur3d.constants import CameraType
from blur3d.api.abstract.abstractscenecamera import AbstractSceneCamera

#-------------------------------------------------------------------------


class StudiomaxSceneCamera(AbstractSceneCamera):

    # For V-Ray Cameras.
    _vRayOutputTypes = ['Still', 'Movie', 'Video']
    _vRayDistortionTypes = ['Quadratic', 'Cubic', 'File', 'Texture']

    # For Physical Cameras.
    _distortionTypes = ['None', 'Cubic', 'Texture']

    #-------------------------------------------------------------------------
    # 												public methods
    #-------------------------------------------------------------------------

    def addProceduralShake(self):

        listController = mxs.getPropertyController(self._nativePointer.controller, 'rotation')
        print mxs.classOf(listController)
        if not mxs.classOf(listController) == mxs.rotation_list:
            listController = mxs.rotation_list()
            mxs.setPropertyController(self._nativePointer.controller, 'rotation', listController)

        noise = mxs.Noise_rotation()
        noise.frequency = 0.05
        noise.fractal = False
        noise.seed = random.randint(0, 10000000)

        # Got lazy here, did not have time to find the Python way to do it.
        maxScript = """fn setNoiseControllerStrength noiseController x y z = (
            noiseController.noise_strength = [x, y, z]
        )"""
        
        mxs.execute(maxScript)
        weirdFactor = 57.296
        mxs.setNoiseControllerStrength(noise, 0.4/weirdFactor, 0.4/weirdFactor, 0.1/weirdFactor)
        mxs.setPropertyController(listController, 'Available', noise)

        return True

    def matchViewport(self, viewport):
        nativeCamera = self.nativePointer()
        nativeTarget = viewport.nativePointer()
        nativeCamera.fov = nativeTarget.getFOV()
        if application.version() >= 16:
            nativeCamera.transform = mxs.InverseHighPrecision(nativeTarget.getTM())
        else: 
            nativeCamera.transform = mxs.Inverse(nativeTarget.getTM())

    def addThreeNodesRig(self):
        """
            \remarks    implements the AbstractScene._createNativeCamera3NodeRig method to return a new 3 node rig
            \param      name            <str>
            \return     <variant> top node of rig
        """
        cam = self.nativePointer()

        # create controls
        pos = mxs.star(radius1 = 6.5, radius2 = 5.5, points=16)
        trans = mxs.rectangle(length=10.2, width=4.5)
        rot = mxs.ngon(radius=2.0, nSides=3, corner_radius=0.5)

        # rename controls
        pos.name = str(cam.name) + 'position'
        trans.name = str(cam.name) + 'translation'
        rot.name = str(cam.name) + 'rotation'

        # rotate controls into place
        pos.rotation = mxs.eulerangles(90, 0 , 0)
        trans.rotation = mxs.eulerangles(90, 0 , 0)
        rot.rotation = mxs.eulerangles(0, 0, -90)

        # reset xforms
        mxs.resetxform(pos)
        mxs.resetxform(trans)
        mxs.resetxform(rot)

        # collapse xforms
        mxs.maxOps.CollapseNode(pos, True)
        mxs.maxOps.CollapseNode(trans, True)
        mxs.maxOps.CollapseNode(rot, True)

        rot.parent = trans
        trans.parent = pos

        pos.wirecolor = rot.wirecolor = trans.wirecolor = mxs.color(0, 230, 250)

        # Move the rig to align with the cam
        pivrot=cam.rotation
        pos.rotation*=pivrot;
        #pos.objectoffsetrot*=pivrot;
        #pos.objectoffsetpos*=pivrot;

        pos.position = cam.position
        #mxs.resetxform(pos)
        #pos.rotation = cam.rotation


        # parent the cam to to rig
        cam.parent = rot

        return True

    def animateTurntable(self, objects=[], startFrame=0, endFrame=100):
        """
                \remarks	Animates the camera around (and properly framing) the given object(s).
                \return		N/A
        """
        if not objects:
            return
        objects = [o.nativePointer() for o in objects]
        cam = self.nativePointer()
        helper = mxs.blur3dhelper.turntableHelperBuilder(
            self.nativePointer(),
            startFrame,
            endFrame,
        )
        # Create an aggregate bounding box for all of our
        # objects so we know how "big" this stuff is, all
        # inclusive.
        from blur3d.lib import cartesian
        aggBBox = None
        for obj in objects:
            p1, p2 = mxs.nodeLocalBoundingBox(obj)
            oBBox = cartesian.BoundingBox(
                cartesian.Point.newFromMaxPoint(p1),
                cartesian.Point.newFromMaxPoint(p2),
            )
            if not aggBBox:
                aggBBox = oBBox
            else:
                aggBBox = cartesian.BoundingBox.union(
                    aggBBox,
                    oBBox,
                )
        # A bounding sphere conveniently gives us a center point.
        center, radius = aggBBox.boundingSphere()
        helper.pos = center.maxPoint()
        # Stick a target object at the center of the objects and
        # rotate it 360 degrees across our frame range, then link
        # the camera to that via a constraint.
        link = mxs.Link_Constraint()
        link.addTarget(helper, 0)
        cam.controller = link
        self.target().nativePointer().pos = center.maxPoint()
        cam.specify_fov = True
        cam.film_width = 36.0
        cam.fov = 40.0
        aspect = float(mxs.renderers.current.image_aspect)
        fovAngle = cartesian.radians(cam.fov)
        axisLength = aggBBox.length(aggBBox.maximumExtent())
        from math import sin, sqrt
        hypoLength = ((axisLength) / sin(fovAngle / 2.0))
        distance = sqrt(
            (hypoLength * hypoLength) - ((axisLength / 2.0) * (axisLength / 2.0)))
        cam.pos = (cam.pos + mxs.point3(0, -distance, 0))

    def cameraType(self):
        """
                \remarks	implements the AbstractSceneCamera.cameraType method to determine what type of camera this instance is
                \return		<blur3d.api.constants.CameraType>
        """
        cls = mxs.classof(self._nativePointer)
        if cls in (mxs.FreeCamera, mxs.TargetCamera):
            return CameraType.Standard

        elif cls == mxs.Physical:
            return CameraType.Physical

        elif cls == mxs.VRayPhysicalCamera:
            return CameraType.Physical
        return 0

    def filmHeight(self):
        """
                \remarks    Returns the film_height of the camera.
                \return     film_height (float)
        """
        cls = mxs.classof(self._nativePointer)
        height = None
        if cls == mxs.VRayPhysicalCamera:

            # TODO: Why is that wrapped in a try except?
            try:
                height = self._nativePointer.film_height
            except AttributeError:
                pass

        elif cls == mxs.Physical:
            height = self._nativePointer.film_height_mm

        if not height:
            # If we failed to get a width from a camera, return the scene aperture setting.
            height = self.filmWidth() * (mxs.renderPixelAspect / mxs.getRendImageAspect())

        return height

    def filmWidth(self):
        """
                \remarks	Returns the film_width of the camera.
                \return		film_width (float)
        """
        cls = mxs.classof(self._nativePointer)
        width = None
        if cls == mxs.VRayPhysicalCamera:
            width = self._nativePointer.film_width

        elif cls == mxs.Physical:
            width = self._nativePointer.film_width_mm

        if not width:
            
            # If we failed to get a width from a camera, return the scene aperture setting.
            width = mxs.getRendApertureWidth()

        return width

    def fov(self, rounded=False):
        """
                \remarks	returns the current FOV of the camera.
                \return		<float>
        """
        fov = self.nativePointer().fov
        if rounded:
            return int(round(fov))
        return fov

    def _nativeFocalLength(self):
        return mxs.cameraFOV.FOVtoMM(self.nativePointer().fov)

    def hasMultiPassEffects(self):
        """
                \remarks	returns whether multipass effects are active on this camera
                \return		<bool>
        """
        cls = mxs.classOf(self._nativePointer)
        if cls in (mxs.VRayPhysicalCamera, mxs.Physical):
            return self._nativePointer.use_DOF
        elif mxs.isProperty(self._nativePointer, 'mpassEnabled'):
            return self._nativePointer.mpassEnabled
        return False

    def readsCache(self):
        return mxs.classOf(self._nativePointer.controller) == mxs.Alembic_Xform

    def renderMultiPassEffects(self):
        """
                \remarks	runs the multipass effects on this camera
                \return		<bool>
        """
        mxs.maxOps.displayActiveCameraViewWithMultiPassEffect()
        return True

    def generateRender(self, **options):
        """
                \remarks	renders an image sequence form that camera with the current render settings
                \param 		path <String>
                \param 		frameRange <blur3d.api.FrameRange>
                \param 		resolution <QtCore.QSize>
                \param 		pixelAspect <float>
                \param 		step <int>
                \param 		missingFramesOnly <bool>
                \return		<blur3d.api.constants.CameraType>
        """

        path = options.get('path', '')
        resolution = options.get(
            'resolution', QSize(mxs.renderWidth, mxs.renderHeight))
        pixelAspect = options.get('pixelAspect', 1.0)
        step = options.get('step', 1)
        frameRange = options.get('frameRange', [])
        missingFramesOnly = options.get('missingFramesOnly', False)

        if path:
            basePath = os.path.split(path)[0]
            if not os.path.exists(basePath):
                os.makedirs(basePath)

        if frameRange:
            bitmap = mxs.render(outputFile=path, fromFrame=frameRange[0], toFrame=frameRange[
                                1], camera=self._nativePointer, nthFrame=step, outputWidth=resolution.width(), outputHeight=resolution.height(), pixelAspect=pixelAspect)
            mxs.undisplay(bitmap)
        else:
            bitmap = mxs.render(outputFile=path, frame=mxs.pyHelper.namify(
                'current'), camera=self._nativePointer, outputWidth=resolution.width(), outputHeight=resolution.height(), pixelAspect=pixelAspect)

    def setFilmWidth(self, width):
        """
                \remarks	Sets the film_width value for the camera.
                \param		width <float>
                \return		n/a
        """
        if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            self._nativePointer.film_width = float(width)
        elif mxs.classOf(self._nativePointer) == mxs.Physical:
            self._nativePointer.film_width_mm = float(width)
        return True

    def outputType(self):
        return self._vRayOutputTypes[self._nativePointer.type] if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera else ''

    def setOutputType(self, outputType):
        if isinstance(outputType, basestring) and mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            self._nativePointer.type = self._vRayOutputTypes.index(outputType)
            return True
        return False

    def exposureEnabled(self):
        return self._nativePointer.exposure if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera else False

    def setExposureEnabled(self, exposureEnabled):
        if isinstance(exposureEnabled, (bool, int, float)) and mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            self._nativePointer.exposure = exposureEnabled
            return True
        return False

    def vignettingEnabled(self):
        if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            return self._nativePointer.vignetting
        elif mxs.classOf(self._nativePointer) == mxs.Physical:
            return self._nativePointer.vignetting_enabled
        return False

    def setVignettingEnabled(self, vignettingEnabled):
        if isinstance(vignettingEnabled, (bool, int, float)):
            classOff = mxs.classOf(self._nativePointer)
            if classOff == mxs.VRayPhysicalCamera:
                self._nativePointer.vignetting = vignettingEnabled
            elif classOff == mxs.Physical:
                self._nativePointer.vignetting_enabled = vignettingEnabled
        return False

    def whiteBalance(self):
        if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            color = self._nativePointer.whiteBalance
        elif mxs.classOf(self._nativePointer) == mxs.Physical:
            color = self._nativePointer.white_balance_custom
        return QColor(color.r, color.g, color.b, color.a) if color else ''

    def setWhiteBalance(self, whiteBalance):
        if isinstance(whiteBalance, QColor):
            if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
                self._nativePointer.whiteBalance_preset = 3
                self._nativePointer.whiteBalance = mxs.Color(*whiteBalance.getRgb())
                return True
            elif mxs.classOf(self._nativePointer) == mxs.Physical:
                self._nativePointer.whiteBalance_type = 0
                self._nativePointer.white_balance_custom = mxs.Color(*whiteBalance.getRgb())
                return True
        return False

    def shutterAngle(self):
        return self._nativePointer.shutter_angle if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera else 180

    def setShutterAngle(self, shutterAngle):
        if isinstance(shutterAngle, (int, float)) and mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            self._nativePointer.shutter_angle = shutterAngle
            return True
        return False

    def shutterOffset(self):
        return self._nativePointer.shutter_offset if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera else 0

    def setShutterOffset(self, shutterOffset):
        if isinstance(shutterOffset, (int, float)) and mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            self._nativePointer.shutter_offset = shutterOffset
            return True
        return False

    def bladesEnabled(self):
        return self._nativePointer.use_blades if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera else False

    def setBladesEnabled(self, bladesEnabled):
        if mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera:
            self._nativePointer.use_blades = bladesEnabled
            return True
        return False

    def blades(self):
        classOf = mxs.classOf(self._nativePointer)
        if classOf == mxs.VRayPhysicalCamera:
            return self._nativePointer.blades_number
        elif classOf == mxs.Physical:
            return self._nativePointer.bokeh_blades_number
        return 0

    def setBlades(self, blades):
        if isinstance(blades, (int, float)):
            classOf = mxs.classOf(self._nativePointer)
            if classOf == mxs.VRayPhysicalCamera:
                self._nativePointer.blades_number = int(blades)
                return True
            elif classOf == mxs.Physical:
                self._nativePointer.bokeh_blades_number = int(blades)
                return True
        return False

    def anisotropy(self):
        classOf = mxs.classOf(self._nativePointer)
        if classOf == mxs.VRayPhysicalCamera:
            return self._nativePointer.anisotropy
        elif classOf == mxs.Physical:
            return self._nativePointer.bokeh_anisotropy
        return False

    # TODO: See if we can do without specifying the identifiers.
    def applyCache(self, path, transformIdentifier, propertiesIdentifier):

        # Applying the controller for transform.
        self._nativePointer.controller = mxs.Alembic_Xform(path=path, identifier=transformIdentifier)
    
        # Creating our own little MAXScript function for things unsupported in Py3dsMax.
        mxs.execute('fn setTimeController obj controller = (obj.controller.time.controller = controller)')

        # Creating the time controller.
        timeController = mxs.Float_Script(script='S')

        # Adding a script controller to alembic time.
        mxs.setTimeController(self._nativePointer, timeController)

        # Creating our own little MAXScript function things unsupported in Py3dsMax.
        maxScript = """fn setAlembicFloatController cam timeController = (
            cam.{prop}.controller = Alembic_Float_Controller()
            cam.{prop}.controller.path = @"{path}"
            cam.{prop}.controller.identifier = @"{identifier}"
            cam.{prop}.controller.property = @"{propertyName}"
            cam.{prop}.controller.time.controller = timeController
            return cam.{prop}.controller.time.controller
        )"""

        # These are the properties we are going to want to load alembic data on.
        cameraType = self.cameraType()
        if cameraType == CameraType.VRayPhysical:

            # We need to create a dedicated radians FOV contoller as the regular FOV controller expects degrees.
            self._addNativeController('RadianFOV', group='Alembic')
            properties = {'Alembic.RadianFOV': 'horizontalFOV', 'clip_near': 'NearClippingPlane', 'clip_far': 'FarClippingPlane', 'focus_distance': 'FocusDistance'}

        else:
            properties = {'fov': 'horizontalFOV', 'nearclip': 'NearClippingPlane', 'farclip': 'FarClippingPlane', 'mpassEffect.focalDepth': 'FocusDistance'}

        for prop in properties:
            mxs.execute(maxScript.format(prop=prop, path=path, identifier=propertiesIdentifier, propertyName=properties[prop]))
            alembicController = mxs.setAlembicFloatController(self._nativePointer, timeController)

        # FOV is going to be special for V-Ray camera.
        if cameraType == CameraType.VRayPhysical:
    
            # Building a script controller for the FOV in degrees.
            scriptController = mxs.float_script()
            scriptController.addtarget('RadianFOV', mxs.getPropertyController(self._nativePointer, "RadianFOV"))

            # Using the radians FOV controller reading the Alembic and converting to degrees.
            scriptController.script = 'radToDeg(RadianFOV)'
            mxs.setPropertyController(self._nativePointer, 'fov', scriptController)

        return True

    def setAnisotropy(self, anisotropy):
        if isinstance(anisotropy, (int, float)):
            classOf = mxs.classOf(self._nativePointer)
            if classOf == mxs.VRayPhysicalCamera:
                self._nativePointer.anisotropy = anisotropy
                return True
            elif classOf == mxs.Physical:
                self._nativePointer.bokeh_anisotropy = anisotropy
                return True
        return False

    def distortionType(self):
        classOf = mxs.classOf(self._nativePointer)
        if classOf == mxs.VRayPhysicalCamera:
            return self._vRayDistortionTypes[self._nativePointer.distortion_type]
        elif classOf == mxs.Physical:
            return self._distortionTypes[self._nativePointer.distortion_type]
        return ''

    def setDistortionType(self, distortionType):
        if isinstance(distortionType, basestring):
            classOf = mxs.classOf(self._nativePointer)
            if classOf == mxs.VRayPhysicalCamera:
                self._nativePointer.distortion_type = self._vRayDistortionTypes.index(distortionType)
                return True
            elif classOf == mxs.Physical:
                self._nativePointer.distortion_type = self._distortionTypes.index(distortionType)
                return True
        return False

    def distortion(self):
        classOf = mxs.classOf(self._nativePointer)
        if classOf == mxs.VRayPhysicalCamera:
            return self._nativePointer.distortion
        elif classOf == mxs.Physical:
            return self._nativePointer.distortion_cubic_amount
        return False

    def setDistortion(self, distortion):
        if isinstance(distortion, (int, float)):
            classOf = mxs.classOf(self._nativePointer)
            if classOf == mxs.VRayPhysicalCamera:
                self._nativePointer.distortion = distortion
                return True               
            elif classOf == mxs.Physical:
                self._nativePointer.distortion_cubic_amount = distortion
                return True
        return False

    def clippingEnabled(self):
        if self.cameraType() == CameraType.Physical:
            return self._nativePointer.clip_on
        else:
            return self._nativePointer.clipManually

    def setClippingEnabled(self, state):
        if self.cameraType() == CameraType.Physical:
            self._nativePointer.clip_on = state
        else:
            self._nativePointer.clipManually = state

    @pendingdeprecation('Use cameraType instead.')
    def isVrayCam(self):
        return mxs.classOf(self._nativePointer) == mxs.VRayPhysicalCamera

    def interest(self):
        if self._nativePointer.Target:
            return blur3d.api.SceneObject(self._scene, self._nativePointer.Target)
        return None

    def setInterest(self, interest):
        if interest:
            if mxs.isproperty(self._nativePointer, "target"):
                self._nativePointer.Target = interest.nativePointer()
            if mxs.isproperty(self._nativePointer, 'targeted'):
                self._nativePointer.Targeted = True
        else:
            if mxs.isproperty(self._nativePointer, "targeted"):
                self._nativePointer.Targeted = False

            # Delete any orphaned targets for this camera.
            target = mxs.findObject(self._nativePointer.name + '.Target')
            while target:
                mxs.delete(target)
                target = mxs.findObject(self._nativePointer.name + '.Target')

    def nearClippingPlane(self):
        if self.cameraType() in (CameraType.VRayPhysical, CameraType.Physical):
            return self.nativePointer().clip_near
        else:
             return self.nativePointer().near_clip

    def farClippingPlane(self):
        if self.cameraType() in (CameraType.VRayPhysical, CameraType.Physical):
            return self.nativePointer().clip_far
        else:
             return self.nativePointer().far_clip

    def _getFrustrumPlanes(self, frame=None, allowClipping=True):
        """Get a list of normal, point tuples that defines the frustum clipping planes"""
        from blur3d.mathutils import Vector, Matrix
        from Py3dsMax import AtTime
        import math
        attime = None
        # Explicit comparison to None in case we need to query frame 0
        if frame != None:
            attime = AtTime()
            attime(frame)
        xform = Matrix.from_MxMatrix(self.nativePointer().objecttransform)

        planes = []
        if self.clippingEnabled() and allowClipping:
            origin = Vector(0,0,0) * xform
            nearClipNormal = Vector(0, 0, -1) * xform
            nearClipNormal -= origin
            nearClipNormal.normalize()
            nearClipPoint = Vector(0, 0, -self.nearClippingPlane()) * xform
            planes.append((nearClipNormal, nearClipPoint))
            farClipNormal = Vector(0, 0, 1) * xform
            farClipNormal -= origin
            farClipNormal.normalize()
            farClipPoint = Vector(0, 0, -self.farClippingPlane()) * xform
            planes.append((farClipNormal, farClipPoint))
        else:
            # We'll hard code the near clipping plane since we don't need to calculate it.
            # Clipping is disabled, so there will be no far clipping
            origin = Vector(0,0,0) * xform
            nearClipNormal = Vector(0, 0, -1) * xform
            nearClipNormal -= origin
            nearClipNormal.normalize()
            nearClipPoint = Vector(0, 0, 0) * xform
            planes.append((nearClipNormal, nearClipPoint))

        fovh = float(self.fov())
        # calculate the vertical fov using the aspect between vertical and horizontal filmback
        fovv = fovh * self.filmHeight() / self.filmWidth()
        # some simple trig to get out x/y coords for the camera view's top-right corner
        x = -1.0 * math.tan(math.radians(fovh * 0.5))
        y = -1.0 * math.tan(math.radians(fovv * 0.5))
        z = -1.0
        origin = Vector((0, 0, 0)) * xform
        # From this we can calculate each corner and get its plane's normal vector
        # We'll use the vector down the camera's frustum and the vector along the image back that
        # define the plane to find a point and normal for that plane.  We'll use the calculated
        # frustum vector for our point, although the camera origin would also be fine.

        # Screen-left clipping
        v1 = Vector((x, y, z)) * xform
        v2 = Vector((0, 1, 0)) * xform
        normal = Vector.PlaneNormal((v1, origin, v2), normalize=True)
        planes.append((normal, v1))

        # Screen-bottom clipping
        x *= -1
        v1 = Vector((x, y, z)) * xform
        v2 = Vector((-1, 0, 0)) * xform
        normal = Vector.PlaneNormal((v1, origin, v2), normalize=True)
        planes.append((normal, v1))

        # Screen-right clipping
        y *= -1
        v1 = Vector((x, y, z)) * xform
        v2 = Vector((0, -1, 0)) * xform
        normal = Vector.PlaneNormal((v1, origin, v2), normalize=True)
        planes.append((normal, v1))

        # Screen-top clipping
        x *= -1
        v1 = Vector((x, y, z)) * xform
        v2 = Vector((1, 0, 0)) * xform
        normal = Vector.PlaneNormal((v1, origin, v2), normalize=True)
        planes.append((normal, v1))

        # Clean up our attime if we used it.
        if attime:
            del attime
        return planes

    def objectsInFrustrum(self, objects=[], considerVisibility=True, frameRange=None, step=1, allowClipping=True):
        from blur3d.api import Scene, SceneCamera, SceneObject
        from Py3dsMax import AtTime
        from blur3d.mathutils import Vector
        # TODO convert objects to SceneObjects?
        
        outputObjects = set()
        if not objects:
            # TODO fill in objects if not specified
            objects = []

        attime = None
        if frameRange == None:
            frameRange = [None]
        else:
            attime = AtTime()

        if isinstance(frameRange, blur3d.api.FrameRange):
            frameRange = xrange(frameRange.start(), frameRange.end()+1, step)
        for frame in frameRange:
            # Explicit comparison to None to allow querying frame 0
            if frame != None:
                attime(frame)

            frustumPlanes = self._getFrustrumPlanes(frame=frame, allowClipping=allowClipping)
            for obj in objects:
                if considerVisibility and obj.isHidden():
                    continue

                boxPoints = [Vector(pnt.x, pnt.y, pnt.z) for pnt in obj.boundingBox().getCorners()]

                for normal, point in frustumPlanes:
                    # false if fully outside, true if inside or intersects
                    # based on code from the amazing iQ
                    # http://www.iquilezles.org/www/articles/frustumcorrect/frustumcorrect.htm
                    out = 0
                    for j in range(8):
                        #print boxPoints[j]
                        # we want to know if dot(N, (P-A)) < 0
                        # we'll get P-Ar
                        vecToP = (boxPoints[j] - point)
                        vecToP.normalize()
                        # and now take the dot product of that vector with our plane's Normal vector
                        out += int( normal.dot(vecToP) < 0 )
                    if out == 8:
                        break
                else:
                    # TODO add extra tests as in iq's pseudocode
                    outputObjects.add(obj)
        if attime:
            del attime
        return list(outputObjects)


# register the symbol
from blur3d import api
api.registerSymbol('SceneCamera', StudiomaxSceneCamera)
