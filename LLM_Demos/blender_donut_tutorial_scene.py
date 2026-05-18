"""
Create a Blender beginner-tutorial-style donut scene programmatically.

Run from Blender's scripting editor, or from a terminal:
    blender --python blender_donut_tutorial_scene.py

The scene includes a torus donut, glossy icing, randomized sprinkles, a plate,
table surface, camera, lights, and Cycles render settings.
"""

import math
import random

import bpy
from mathutils import Vector


SEED = 42
DONUT_BROWN = (0.55, 0.30, 0.13, 1.0)
DONUT_DARK = (0.34, 0.16, 0.06, 1.0)
ICING_PINK = (1.0, 0.42, 0.63, 1.0)
PLATE_WHITE = (0.92, 0.88, 0.80, 1.0)
TABLE_WOOD = (0.48, 0.31, 0.18, 1.0)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_material(name, color, roughness=0.45, metallic=0.0, specular=0.5):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Specular IOR Level"].default_value = specular
    return material


def add_torus(name, material, major_radius, minor_radius, location, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=192,
        minor_segments=48,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj


def add_donut(donut_material, icing_material):
    donut = add_torus(
        "Golden cake donut",
        donut_material,
        major_radius=1.35,
        minor_radius=0.46,
        location=(0, 0, 0.68),
    )
    donut.scale.z = 0.58

    icing = add_torus(
        "Pink icing",
        icing_material,
        major_radius=1.34,
        minor_radius=0.34,
        location=(0, 0, 0.90),
    )
    icing.scale.z = 0.18

    # A slight vertical offset and flattened torus gives the icing a draped cap
    # rather than a full tube wrapped evenly around the donut.
    icing.modifiers.new("Glossy icing subdivision", "SUBSURF").levels = 1
    return donut, icing


def add_icing_drips(icing_material):
    drips = [
        (0.25, 1.16, 0.20),
        (1.08, 0.43, 0.27),
        (0.77, -0.92, 0.23),
        (-0.48, -1.12, 0.31),
        (-1.20, -0.18, 0.24),
        (-0.82, 0.80, 0.20),
    ]

    for index, (x, y, length) in enumerate(drips, start=1):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=32,
            ring_count=16,
            radius=0.18,
            location=(x, y, 0.74 - length * 0.18),
        )
        drip = bpy.context.object
        drip.name = f"Icing drip {index}"
        drip.scale = (0.78, 0.52, 1.15 + length)
        drip.data.materials.append(icing_material)
        bpy.ops.object.shade_smooth()


def add_sprinkle(material, location, angle, length=0.22, radius=0.018):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=radius,
        depth=length,
        location=location,
        rotation=(math.radians(82), 0, angle),
    )
    sprinkle = bpy.context.object
    sprinkle.name = "Sprinkle"
    sprinkle.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return sprinkle


def add_sprinkles(materials, count=120):
    rng = random.Random(SEED)
    sprinkle_materials = list(materials)

    for _ in range(count):
        theta = rng.uniform(0, math.tau)
        ring_radius = rng.uniform(0.62, 1.54)

        # Skip the center hole so sprinkles sit on icing only.
        if 0.84 < ring_radius < 1.08 and rng.random() < 0.55:
            ring_radius += 0.32

        x = math.cos(theta) * ring_radius
        y = math.sin(theta) * ring_radius
        z = 1.02 + rng.uniform(-0.015, 0.055)
        angle = rng.uniform(0, math.tau)
        material = rng.choice(sprinkle_materials)
        add_sprinkle(material, (x, y, z), angle)


def add_plate_and_table(plate_material, table_material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=2.25, depth=0.16, location=(0, 0, 0.18))
    plate = bpy.context.object
    plate.name = "Simple ceramic plate"
    plate.data.materials.append(plate_material)
    bpy.ops.object.shade_smooth()

    bevel = plate.modifiers.new("Plate rounded rim", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 8
    plate.modifiers.new("Plate weighted normals", "WEIGHTED_NORMAL")

    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.82,
        minor_radius=0.06,
        major_segments=160,
        minor_segments=16,
        location=(0, 0, 0.30),
    )
    rim = bpy.context.object
    rim.name = "Raised plate rim"
    rim.data.materials.append(plate_material)
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, -0.02))
    table = bpy.context.object
    table.name = "Wood table"
    table.dimensions = (7.0, 7.0, 0.12)
    table.data.materials.append(table_material)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def add_lights():
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -4.0, 5.2))
    key = bpy.context.object
    key.name = "Large soft key light"
    key.data.energy = 520
    key.data.size = 4.0

    bpy.ops.object.light_add(type="POINT", location=(3.2, 2.4, 2.6))
    fill = bpy.context.object
    fill.name = "Small sprinkle glint"
    fill.data.energy = 75


def point_camera_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera():
    bpy.ops.object.camera_add(location=(3.4, -4.6, 2.8))
    camera = bpy.context.object
    point_camera_at(camera, (0, 0, 0.72))
    camera.data.lens = 58
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 5.6
    camera.data.dof.aperture_fstop = 6.3
    bpy.context.scene.camera = camera


def setup_render():
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.world.color = (0.04, 0.04, 0.045)
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1200


def main():
    clear_scene()

    donut = make_material("Baked donut dough", DONUT_BROWN, roughness=0.62, specular=0.3)
    icing = make_material("Glossy strawberry icing", ICING_PINK, roughness=0.25, specular=0.85)
    plate = make_material("Warm ceramic plate", PLATE_WHITE, roughness=0.34, specular=0.55)
    table = make_material("Walnut table", TABLE_WOOD, roughness=0.58, specular=0.25)

    sprinkle_materials = [
        make_material("White sprinkle", (0.98, 0.94, 0.86, 1), roughness=0.32),
        make_material("Yellow sprinkle", (1.0, 0.82, 0.18, 1), roughness=0.32),
        make_material("Blue sprinkle", (0.12, 0.45, 0.95, 1), roughness=0.32),
        make_material("Green sprinkle", (0.18, 0.78, 0.34, 1), roughness=0.32),
        make_material("Red sprinkle", (0.95, 0.10, 0.13, 1), roughness=0.32),
    ]

    add_plate_and_table(plate, table)
    add_donut(donut, icing)
    add_icing_drips(icing)
    add_sprinkles(sprinkle_materials)
    add_lights()
    setup_camera()
    setup_render()


if __name__ == "__main__":
    main()
