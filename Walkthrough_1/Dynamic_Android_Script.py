# May 19 2026 - Mrudang Mathur
# Surigcal Intelligence and Modeling Lab - Stanford University 

import bpy
from mathutils import *
from math import *

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
    
# CLEAR WORKSPACE OF UNWANTED OBJECTS
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()

#pathName = os.path.dirname(os.path.abspath(__file__)) + "/PLY/"
pathName = "PrecedingDirectoryHere/BIOS444_Sp26/Walkthrough_1/PLY/"

# LOAD ALL PLY FILES 
fileName = "Valve"
startFrame = 0 # File no. of first object in timeseries
endFrame = 20 # File no. of last object in timeseries
numRange = range(startFrame,endFrame+1)

isoScale = 0.1 # Isotropic scaling factor for object size
objLocation = (0.,0.,2.25) # Object location

init_frame = 1 # Frame no. of first frame in animation
animStep = 2 # No. of empty frames between two meshes in animation; like "frame-rate"
count = 1

outputName = pathName+"/"+fileName+"_Dynamic.glb" # Output file name

for i in numRange:
    
    # IMPORT OBJECTS 
    tempfileName = pathName+fileName+"_"+str(i)+".ply"
    print(tempfileName)
    bpy.ops.wm.ply_import(filepath=tempfileName)
    
    # TRANSFORM OBJECTS
    bpy.context.object.scale = (isoScale,isoScale,isoScale)
    bpy.context.object.location = objLocation
    bpy.ops.object.shade_smooth()

    # ADD COLOUR MAP 
    temp_matName = "Material_"+str(i)
    new_mat = bpy.data.materials.new(name=temp_matName)
    bpy.context.object.data.materials.append(new_mat)
    new_mat.use_nodes = True
    nodes = new_mat.node_tree.nodes
    material_output = nodes.get("Material Output")
    material_input = nodes.get("Material Input")
    node_attribute = nodes.new(type="ShaderNodeAttribute")
    node_attribute.attribute_name = "Col"
    new_mat.node_tree.links.new(node_attribute.outputs[0], bpy.data.materials[temp_matName].node_tree.nodes["Principled BSDF"].inputs[0])

    # DECIMATE GEOMETRY (TO REDUCE FINAL FILESIZE)
    #bpy.ops.object.modifier_add(type='DECIMATE')
    #bpy.context.object.modifiers["Decimate"].ratio = 0.25


# CREATE SHARED ACTION FOR ALL OBJECTS
shared_action = bpy.data.actions.new(name="Dynamic_Animation")

for i in range(startFrame, endFrame + 1):
    obj_name = fileName + "_" + str(i)
    obj = bpy.data.objects[obj_name]

    if obj.animation_data is None:
        obj.animation_data_create()

    obj.animation_data.action = shared_action

# ANIMATE OBJECT SCALE
for i in range(startFrame,endFrame):

    tempName = fileName+"_"+str(i)

    bpy.data.objects[fileName+"_"+str(i)].scale = [isoScale,isoScale,isoScale]
    bpy.data.objects[fileName+"_"+str(i)].keyframe_insert(data_path = "scale", frame = count)
    bpy.data.objects[fileName+"_"+str(i+1)].scale = [0.0,0.0,0.0]
    bpy.data.objects[fileName+"_"+str(i+1)].keyframe_insert(data_path = "scale", frame = count)

    bpy.data.objects[fileName+"_"+str(i)].scale = [0.0,0.0,0.0]
    bpy.data.objects[fileName+"_"+str(i)].keyframe_insert(data_path = "scale", frame = count+animStep)
    bpy.data.objects[fileName+"_"+str(i+1)].scale = [isoScale,isoScale,isoScale]
    bpy.data.objects[fileName+"_"+str(i+1)].keyframe_insert(data_path = "scale", frame = count+animStep)
    
    count = count+animStep
  
# ADJUST INTERPOLATION CURVES     
for obj in bpy.data.objects:
    action = obj.animation_data.action

    # Older Blender API
    if hasattr(action, "fcurves"):
        for fcurve in action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = "CONSTANT"

    # Newer Blender API with layers/strips
    if hasattr(action, "layers"):
        
        for dim in range(0,3):
            fcurve = action.fcurve_ensure_for_datablock(obj,\
                 "scale",index=dim)  
            for kf in fcurve.keyframe_points:
                kf.interpolation = "CONSTANT"  

# ADJUST FRAME RANGE OF ANIMATION
bpy.context.scene.frame_end = init_frame + (endFrame-startFrame+1)*animStep

# ADD LIGHTING
#light_data = bpy.data.lights.new(name="my-light-data", type='POINT')
#light_data.energy = 100
#light_object = bpy.data.objects.new(name="LIGHT", object_data=light_data)
#bpy.context.collection.objects.link(light_object)
#light_object.location = (0, 0, 0.5)
#bpy.data.collections['Collection'].objects['LIGHT'].select_set(True)

# EXPORT FILE
bpy.ops.export_scene.gltf(filepath = outputName, export_nla_strips=False)