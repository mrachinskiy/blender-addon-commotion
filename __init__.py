# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Commotion motion graphics add-on for Blender.
#  Copyright (C) 2014-2020  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Commotion",
    "author": "Mikhail Rachinskiy",
    "version": (2, 2, 0),
    "blender": (2, 90, 0),
    "location": "3D View > Sidebar",
    "description": "Animation offset tools for motion graphics.",
    "doc_url": "https://github.com/mrachinskiy/commotion#readme",
    "tracker_url": "https://github.com/mrachinskiy/commotion/issues",
    "category": "Animation",
}


if "bpy" in locals():
    import os
    from typing import Dict
    from types import ModuleType

    from . import var


    def reload_recursive(path: str, mods: Dict[str, ModuleType]) -> None:
        import importlib

        for entry in os.scandir(path):

            if entry.is_file() and entry.name.endswith(".py") and not entry.name.startswith("__"):
                filename, _ = os.path.splitext(entry.name)

                if filename in mods:
                    importlib.reload(mods[filename])

            elif entry.is_dir() and not entry.name.startswith((".", "__")):

                if entry.name in mods:
                    importlib.reload(mods[entry.name])
                    reload_recursive(entry.path, mods[entry.name].__dict__)
                    continue

                reload_recursive(entry.path, mods)


    reload_recursive(var.ADDON_DIR, locals())
else:
    import bpy
    from bpy.props import PointerProperty

    from . import (
        preferences,
        op_offset,
        ops_anim,
        ops_proxy,
        ops_shapekey,
        ui,
        mod_update,
    )


classes = (
    preferences.CommotionShapeKeyCollection,
    preferences.CommotionPreferences,
    preferences.SceneProperties,
    preferences.WmProperties,
    ui.VIEW3D_MT_commotion,
    ui.VIEW3D_PT_commotion_update,
    ui.VIEW3D_PT_commotion_animation_offset,
    ui.VIEW3D_PT_commotion_animation_utils,
    ui.VIEW3D_PT_commotion_shape_keys,
    ui.VIEW3D_PT_commotion_proxy_effector,
    ui.VIEW3D_PT_commotion_proxy_effector_loc,
    ui.VIEW3D_PT_commotion_proxy_effector_rot,
    ui.VIEW3D_PT_commotion_proxy_effector_sca,
    ui.VIEW3D_PT_commotion_proxy_effector_sk,
    ui.VIEW3D_PT_commotion_proxy_effector_bake,
    op_offset.ANIM_OT_animation_offset,
    op_offset.ANIM_OT_animation_offset_eyedropper,
    ops_shapekey.OBJECT_OT_sk_coll_refresh,
    ops_shapekey.OBJECT_OT_sk_interpolation_set,
    ops_shapekey.ANIM_OT_sk_generate_keyframes,
    ops_anim.ANIM_OT_animation_copy,
    ops_anim.ANIM_OT_animation_link,
    ops_anim.ANIM_OT_animation_convert,
    ops_proxy.ANIM_OT_bake,
    ops_proxy.ANIM_OT_bake_remove,
    *mod_update.ops,
)


def register():
    if bl_info["blender"] > bpy.app.version:
        addon_name = bl_info["name"].upper()
        addon_ver = ".".join(str(x) for x in bl_info["version"])
        blender_ver = ".".join(str(x) for x in bl_info["blender"][:2])
        requirements_check = RuntimeError(
            f"\n!!! BLENDER {blender_ver} IS REQUIRED FOR {addon_name} {addon_ver} !!!"
            "\n!!! READ INSTALLATION GUIDE !!!"
        )
        raise requirements_check

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.commotion = PointerProperty(type=preferences.SceneProperties)
    bpy.types.WindowManager.commotion = PointerProperty(type=preferences.WmProperties)

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.append(ui.draw_commotion_menu)

    # mod_update
    # ---------------------------

    mod_update.init(
        addon_version=bl_info["version"],
        repo_url="mrachinskiy/commotion",
    )


def unregister():
    from . import proxy_effector

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.commotion
    del bpy.types.WindowManager.commotion

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object.remove(ui.draw_commotion_menu)

    # Handlers
    # ---------------------------

    proxy_effector.handler_del()


if __name__ == "__main__":
    register()
