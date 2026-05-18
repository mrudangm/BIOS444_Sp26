"""
Create a stylized 3D Stanford-inspired logo in Blender.

Run from Blender's scripting editor, or from a terminal:
    blender --python stanford_logo_3d_blender.py

This script builds a dimensional cardinal "S" with layered white/black backing
and a simple green tree element. It is a fan-made procedural interpretation,
not an official Stanford asset.
"""

import math
import os
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


CARDINAL_RED = (0.55, 0.02, 0.05, 1.0)
DARK_RED = (0.20, 0.00, 0.02, 1.0)
WHITE = (0.96, 0.94, 0.90, 1.0)
BLACK = (0.015, 0.012, 0.011, 1.0)
TREE_GREEN = (0.03, 0.31, 0.12, 1.0)
TREE_DARK = (0.01, 0.13, 0.05, 1.0)
BARK = (0.30, 0.13, 0.04, 1.0)
GOLD = (0.95, 0.70, 0.18, 1.0)

# Put your Varsity Block .ttf/.otf next to this script, or set:
#     VARSITY_BLOCK_FONT_PATH=/absolute/path/to/VarsityBlock.ttf
SCRIPT_DIR = Path(__file__).resolve().parent
VARSITY_BLOCK_FONT_CANDIDATES = [
    os.environ.get("VARSITY_BLOCK_FONT_PATH"),
    SCRIPT_DIR / "VarsityBlock.ttf",
    SCRIPT_DIR / "VarsityBlock.otf",
    SCRIPT_DIR / "Varsity Block.ttf",
    SCRIPT_DIR / "Varsity Block.otf",
    Path.home() / "Downloads" / "varsity_regular.ttf",
    Path.home() / "Downloads" / "VarsityBlock.ttf",
    Path.home() / "Downloads" / "Varsity Block.ttf",
]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_material(name, color, roughness=0.45, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return material


def load_varsity_block_font():
    for candidate in VARSITY_BLOCK_FONT_CANDIDATES:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.exists():
            return bpy.data.fonts.load(str(path))

    print("Varsity Block font file not found; using procedural block-letter S.")
    return None


def add_logo_text(name, text, material, scale, y, extrusion, bevel, font):
    bpy.ops.object.text_add(
        location=(0, y, 0),
        rotation=(math.radians(90), 0, 0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = 4.4
    obj.data.font = font
    obj.data.extrude = extrusion
    obj.data.bevel_depth = bevel
    obj.data.bevel_resolution = 3
    obj.scale = (scale, scale, scale)
    obj.data.materials.append(material)
    return obj


def add_block_piece(name, material, location, dimensions, bevel_width):
    bpy.ops.mesh.primitive_cube_add(location=location)
    piece = bpy.context.object
    piece.name = name
    piece.dimensions = dimensions
    piece.data.materials.append(material)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bevel = piece.modifiers.new("Varsity bevel", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 2
    piece.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return piece


def add_procedural_block_s_layer(name, material, scale, y, depth, bevel):
    """Create a varsity-style block S from beveled slab pieces."""
    pieces = [
        ("top bar", (0.0, 1.28), (2.42, 0.56)),
        ("upper left stroke", (-0.90, 0.66), (0.58, 1.08)),
        ("middle bar", (0.0, 0.02), (2.20, 0.54)),
        ("lower right stroke", (0.90, -0.66), (0.58, 1.08)),
        ("bottom bar", (0.0, -1.28), (2.42, 0.56)),
        ("top left serif", (-1.24, 1.58), (0.58, 0.36)),
        ("top right serif", (1.24, 0.98), (0.58, 0.36)),
        ("middle left serif", (-1.12, -0.28), (0.50, 0.34)),
        ("middle right serif", (1.12, 0.32), (0.50, 0.34)),
        ("bottom left serif", (-1.24, -0.98), (0.58, 0.36)),
        ("bottom right serif", (1.24, -1.58), (0.58, 0.36)),
    ]

    created = []
    for label, (x, z), (width, height) in pieces:
        created.append(
            add_block_piece(
                f"{name} {label}",
                material,
                location=(x * scale, y, z * scale),
                dimensions=(width * scale, depth, height * scale),
                bevel_width=bevel,
            )
        )
    return created


def add_logo_s_layers(red, white, black):
    varsity_block_font = load_varsity_block_font()
    if varsity_block_font:
        add_logo_text(
            "Black outer S",
            "S",
            black,
            scale=1.18,
            y=0.12,
            extrusion=0.18,
            bevel=0.018,
            font=varsity_block_font,
        )
        add_logo_text(
            "White inner outline S",
            "S",
            white,
            scale=1.08,
            y=-0.02,
            extrusion=0.16,
            bevel=0.015,
            font=varsity_block_font,
        )
        add_logo_text(
            "Cardinal red front S",
            "S",
            red,
            scale=0.96,
            y=-0.18,
            extrusion=0.22,
            bevel=0.012,
            font=varsity_block_font,
        )
        return

    add_procedural_block_s_layer("Black outer S", black, scale=1.18, y=0.12, depth=0.28, bevel=0.045)
    add_procedural_block_s_layer("White inner outline S", white, scale=1.08, y=-0.02, depth=0.25, bevel=0.038)
    add_procedural_block_s_layer("Cardinal red front S", red, scale=0.96, y=-0.18, depth=0.30, bevel=0.032)


def add_extruded_polygon(name, material, points, y, depth, scale=1.0, bevel=0.0):
    """Create a shallow 3D logo piece from front-facing X/Z polygon points."""
    half_depth = depth / 2
    front = [(x * scale, y - half_depth, z * scale) for x, z in points]
    back = [(x * scale, y + half_depth, z * scale) for x, z in points]
    vertices = front + back
    count = len(points)
    triangles = tessellate_polygon([[Vector((x * scale, z * scale, 0.0)) for x, z in points]])
    faces = []

    for triangle in triangles:
        faces.append(tuple(triangle))
        faces.append(tuple(index + count for index in reversed(triangle)))

    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, next_index + count, index + count))

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)

    if bevel:
        bevel_modifier = obj.modifiers.new("Small logo bevel", "BEVEL")
        bevel_modifier.width = bevel
        bevel_modifier.segments = 2
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_tree(materials):
    """Build a Stanford-logo-inspired tree silhouette with layered outlines."""
    green, dark_green, bark, gold, white, black = materials
    del dark_green, bark, gold

    tree_points = [
        (0.00, 2.05),
        (-0.08, 1.86),
        (-0.02, 1.84),
        (-0.17, 1.71),
        (-0.08, 1.69),
        (-0.28, 1.53),
        (-0.13, 1.54),
        (-0.39, 1.32),
        (-0.19, 1.36),
        (-0.55, 1.08),
        (-0.28, 1.15),
        (-0.67, 0.83),
        (-0.36, 0.94),
        (-0.78, 0.57),
        (-0.42, 0.72),
        (-0.86, 0.30),
        (-0.46, 0.48),
        (-0.83, 0.08),
        (-0.43, 0.24),
        (-0.78, -0.16),
        (-0.38, 0.00),
        (-0.68, -0.36),
        (-0.32, -0.22),
        (-0.54, -0.62),
        (-0.27, -0.52),
        (-0.24, -1.02),
        (-0.42, -1.34),
        (-0.50, -1.62),
        (0.50, -1.62),
        (0.42, -1.34),
        (0.24, -1.02),
        (0.27, -0.52),
        (0.54, -0.62),
        (0.32, -0.22),
        (0.68, -0.36),
        (0.38, 0.00),
        (0.78, -0.16),
        (0.43, 0.24),
        (0.83, 0.08),
        (0.46, 0.48),
        (0.86, 0.30),
        (0.42, 0.72),
        (0.78, 0.57),
        (0.36, 0.94),
        (0.67, 0.83),
        (0.28, 1.15),
        (0.55, 1.08),
        (0.19, 1.36),
        (0.39, 1.32),
        (0.13, 1.54),
        (0.28, 1.53),
        (0.08, 1.69),
        (0.17, 1.71),
        (0.02, 1.84),
        (0.08, 1.86),
    ]

    add_extruded_polygon("Tree black keyline", black, tree_points, y=-0.83, depth=0.070, scale=0.88, bevel=0.012)
    add_extruded_polygon("Tree white outline", white, tree_points, y=-0.875, depth=0.075, scale=0.82, bevel=0.012)
    add_extruded_polygon("Tree green face", green, tree_points, y=-0.93, depth=0.085, scale=0.76, bevel=0.010)


def add_base_and_lighting(materials):
    _, _, _, _, _, dark_red = materials

    bpy.ops.mesh.primitive_cube_add(location=(0, 0.22, -1.55))
    base = bpy.context.object
    base.name = "Cardinal beveled pedestal"
    base.dimensions = (4.8, 0.65, 0.22)
    base.data.materials.append(dark_red)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = base.modifiers.new("Soft bevel", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 5
    base.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")

    bpy.ops.object.light_add(type="AREA", location=(0, -4.5, 5.5))
    key = bpy.context.object
    key.name = "Large softbox"
    key.data.energy = 520
    key.data.size = 4.5

    bpy.ops.object.light_add(type="POINT", location=(-3.3, -2.2, 1.7))
    fill = bpy.context.object
    fill.name = "Small red rim light"
    fill.data.energy = 80
    fill.data.color = (1.0, 0.25, 0.25)


def point_camera_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera():
    bpy.ops.object.camera_add(location=(0, -8.0, 2.2))
    camera = bpy.context.object
    point_camera_at(camera, (0, -0.15, 0.05))
    camera.data.lens = 58
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 7.6
    camera.data.dof.aperture_fstop = 7.0
    bpy.context.scene.camera = camera


def setup_render():
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 96
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.world.color = (0.025, 0.025, 0.03)
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1600


def main():
    clear_scene()

    red = make_material("Stanford cardinal red", CARDINAL_RED)
    white = make_material("Warm white outline", WHITE)
    black = make_material("Black outer outline", BLACK)
    green = make_material("Tree green", TREE_GREEN)
    dark_green = make_material("Tree shadow green", TREE_DARK)
    bark = make_material("Tree bark", BARK)
    gold = make_material("Tree top highlight", GOLD, roughness=0.3, metallic=0.15)
    dark_red = make_material("Dark cardinal side", DARK_RED)

    # Prefer a real Varsity Block font file, then use a procedural block S.
    add_logo_s_layers(red, white, black)

    add_tree((green, dark_green, bark, gold, white, black))
    add_base_and_lighting((red, white, black, green, dark_green, dark_red))
    setup_camera()
    setup_render()

    # Smooth all mesh objects for a polished render while leaving text curves intact.
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
            obj.select_set(False)


if __name__ == "__main__":
    main()
