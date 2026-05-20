# May 19 2026 - Mrudang Mathur
# Surigcal Intelligence and Modeling Lab - Stanford University 

import bpy
from mathutils import *
from math import *
import os
from pathlib import Path

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# CLEAR WORKSPACE OF UNWANTED OBJECTS    
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()
bpy.ops.outliner.orphans_purge()

#pathName = os.path.dirname(os.path.abspath(__file__)) + "/PLY/"
pathName = "PrecedingDirectoryHere/BIOS444_Sp26/Walkthrough_1/PLY/"

# LOAD ALL PLY FILES 
fileName = "Valve_USDZ"
startFrame = 1 # File no. of first object in timeseries
endFrame = 20 # File no. of last object in timeseries
numRange = range(endFrame,startFrame-1,-1)

isoScale = 0.1 # Isotropic scaling factor for object size
objLocation = (0.,0.,2.25) # Object location

key_index = 1 # File no. of first object in timeseries
init_frame = 1 # Frame no. of first frame in animation
step  = 2 # No. of empty frames between two meshes in animation; like "frame-rate"
nloops = 2 # No. of loops in animation

outputName = pathName+"/"+fileName+"_Dynamic.usdz" # Output file name

# Texture baking settings
BAKE_TEXTURES = True
TEXTURE_RESOLUTION = 1024
BAKE_TYPE = "EMIT"   # best for preserving scientific colormaps
BAKE_MARGIN = 8

bake_dir = Path(pathName) / "baked_textures"
bake_dir.mkdir(parents=True, exist_ok=True)

#SETUP BAKING
bpy.context.scene.render.engine = "CYCLES"
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.bake.use_clear = True
bpy.context.scene.render.bake.margin = BAKE_MARGIN

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def ensure_uv(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")

def make_vertex_color_emit_material(obj, mat_name):
    """
    Creates material:
    Attribute 'Col' -> Emission Color -> Material Output

    This is useful because EMIT bake preserves your vertex colors
    without lighting/shading effects.
    """
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    attr = nodes.new(type="ShaderNodeAttribute")
    attr.attribute_name = "Col"

    emission = nodes.new(type="ShaderNodeEmission")
    out = nodes.new(type="ShaderNodeOutputMaterial")

    links.new(attr.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], out.inputs["Surface"])

    obj.data.materials.clear()
    obj.data.materials.append(mat)

    return mat

def bake_object_to_png(obj, image_name, out_path):
    """
    Bakes the object's current material to a PNG and returns the image.
    """
    ensure_uv(obj)

    image = bpy.data.images.new(
        name=image_name,
        width=TEXTURE_RESOLUTION,
        height=TEXTURE_RESOLUTION,
        alpha=True
    )

    # Add bake target image node to every material.
    # Blender bakes into the active selected Image Texture node.
    for mat in obj.data.materials:
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.name = f"{obj.name}_BakeTarget"
        tex_node.image = image

        for node in nodes:
            node.select = False

        tex_node.select = True
        nodes.active = tex_node

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.bake(type=BAKE_TYPE)

    image.filepath_raw = str(out_path)
    image.file_format = "PNG"
    image.save()

    return image

def replace_with_baked_texture_material(obj, image):
    """
    Replaces material with:
    Image Texture -> Principled BSDF Base Color -> Material Output
    """
    mat = bpy.data.materials.new(name=f"{obj.name}_BakedMaterial")
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    tex = nodes.new(type="ShaderNodeTexImage")
    tex.image = image

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    out = nodes.new(type="ShaderNodeOutputMaterial")

    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    obj.data.materials.clear()
    obj.data.materials.append(mat)

    return mat


counter = init_frame 

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
    make_vertex_color_emit_material(bpy.context.object, temp_matName)

    # BAKE VERTEX COLORS TO PNG FILE
    if BAKE_TEXTURES:
        baked_path = bake_dir / f"{fileName}_{i}_baked.png"

        image = bake_object_to_png(
            obj=bpy.context.object,
            image_name=f"{fileName}_{i}_BakedTexture",
            out_path=baked_path
        )

        replace_with_baked_texture_material(bpy.context.object, image)


# ANIMATE OBJECTS

for obj in bpy.data.collections['Collection'].all_objects:
    obj.select_set(True)

bpy.ops.object.join_shapes()

for j in range(0,nloops):

    for i in range(startFrame+1,endFrame+1):

        tempName = fileName+"_"+str(i)
        bpy.context.object.active_shape_key_index = key_index
        bpy.data.shape_keys["Key"].key_blocks[tempName].value = 0
        bpy.data.shape_keys["Key"].key_blocks[tempName].keyframe_insert("value",frame=counter)
        bpy.data.shape_keys["Key"].key_blocks[tempName].value = 1
        bpy.data.shape_keys["Key"].key_blocks[tempName].keyframe_insert("value",frame=counter+step)
        bpy.data.shape_keys["Key"].key_blocks[tempName].value = 0
        bpy.data.shape_keys["Key"].key_blocks[tempName].keyframe_insert("value",frame=counter+2*step)

        counter = counter+step
        key_index = key_index+1

bpy.context.scene.frame_end = init_frame + (endFrame-startFrame)*step*nloops+step

for obj in bpy.data.collections['Collection'].all_objects:
    obj.select_set(False)

#bpy.ops.object.select_all(action='TOGGLE')

# DELETE EXTRA FRAMES
for i in range(endFrame,startFrame,-1):
    bpy.data.objects[fileName+"_"+str(i)].select_set(True)
    bpy.ops.object.delete()

# ADD LIGHTING
#light_data = bpy.data.lights.new(name="my-light-data", type='POINT')
#light_data.energy = 100
#light_object = bpy.data.objects.new(name="LIGHT", object_data=light_data)
#bpy.context.collection.objects.link(light_object)
#light_object.location = (0, 0, 0.5)
#bpy.data.collections['Collection'].objects['LIGHT'].select_set(True)

bpy.data.collections['Collection'].objects[fileName+"_"+str(startFrame)].select_set(True)

bpy.ops.wm.usd_export(filepath= outputName, export_animation= True, selected_objects_only = True)

