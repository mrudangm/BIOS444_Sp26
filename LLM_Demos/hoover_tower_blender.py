"""
Create a stylized 3D model of Hoover Tower at Stanford University.
Run from Blender's scripting editor, or from a terminal:
    blender --python hoover_tower_blender.py
"""

import bpy
import math
from mathutils import Vector

# Colors
SANDSTONE = (0.75, 0.65, 0.50, 1.0)
DARK_SANDSTONE = (0.55, 0.45, 0.30, 1.0)
HOOVER_RED = (0.6, 0.1, 0.1, 1.0)  # Reddish tone for the dome
WINDOW_GLASS = (0.1, 0.2, 0.3, 1.0)

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def make_material(name, color, roughness=0.6, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return material

def add_cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj

def build_hoover_tower():
    clear_scene()
    
    # Materials
    mat_sand = make_material("Sandstone", SANDSTONE)
    mat_red = make_material("Hoover Red", HOOVER_RED, roughness=0.4)
    mat_glass = make_material("Glass", WINDOW_GLASS, roughness=0.1, metallic=0.1)

    # 1. Main Base Section
    base = add_cube("Tower_Base", (0, 0, 2), (5, 5, 2), mat_sand)
    
    # 2. Main Shaft
    shaft = add_cube("Tower_Shaft", (0, 0, 15), (3, 3, 13), mat_sand)
    
    # 3. Top Observation Deck / Crown
    crown = add_cube("Tower_Crown", (0, 0, 28), (3.2, 3.2, 1), mat_sand)
    
    # 4. The Red Dome
    # Using a sphere scaled into a dome shape
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.2, location=(0, 0, 29))
    dome = bpy.context.object
    dome.name = "Tower_Dome"
    dome.scale = (1, 1, 0.6) # Flatten it into a dome
    dome.data.materials.append(mat_red)

    # 5. The Sandstone Spire (on top of the dome)
    bpy.ops.mesh.primitive_cone_add(radius1=0.4, radius2=0, depth=4, location=(0, 0, 31))
    spire = bpy.context.object
    spire.name = "Tower_Spire"
    spire.data.materials.append(mat_sand)

    # 6. Adding stylized "windows" (slots)
    for i in range(4):
        offsets = [(3.1, 0), (-3.1, 0), (0, 3.1), (0, -3.1)]
        off_x, off_y = offsets[i]
        win = add_cube(f"Window_{i}", (off_x, off_y, 15), (0.1, 0.5, 10), mat_glass)

    # Lighting & Camera
    bpy.ops.object.light_add(type="SUN", location=(10, 10, 20))
    bpy.context.object.data.energy = 5

    bpy.ops.object.camera_add(location=(30, -30, 15))
    cam = bpy.context.object
    direction = Vector((0, 0, 10)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam

    # Render Settings
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.world.color = (0.5, 0.7, 1.0)

    # Smoothing
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()

if __name__ == "__main__":
    build_hoover_tower()

