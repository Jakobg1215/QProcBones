
import bpy
import inspect

from . import properties
from . import panels
from . import operators

bl_info = {
    "name": "Quaternion Procedural Bones",
    "description": "A panel that helps create procedural bones for source engine models.",
    "author": "Jakobg1215",
    "version": (1, 2),
    "blender": (4, 0, 0),
    "location": "View3D > QProcBones",
    "tracker_url": "https://github.com/Jakobg1215/qprocbones/issues",
    "category": "Rigging"
}


def register() -> None:
    all_properties_classes = inspect.getmembers(properties, inspect.isclass)
    property_classes = [cls for name, cls in all_properties_classes if issubclass(cls, bpy.types.PropertyGroup)]
    property_classes.reverse()
    for property_class in property_classes:
        bpy.utils.register_class(property_class)

    all_operator_classes = inspect.getmembers(operators, inspect.isclass)
    operator_classes = [cls for name, cls in all_operator_classes if issubclass(cls, bpy.types.Operator)]
    operator_classes.reverse()
    for operator_class in operator_classes:
        bpy.utils.register_class(operator_class)

    all_panel_classes = inspect.getmembers(panels, inspect.isclass)
    panel_classes = [cls for name, cls in all_panel_classes if issubclass(cls, bpy.types.Panel)]
    panel_classes.reverse()
    for panel_class in panel_classes:
        bpy.utils.register_class(panel_class)

    bpy.types.Object.procedural_bones = bpy.props.PointerProperty(type=properties.ProceduralBonesDataProperty)


def unregister() -> None:
    all_properties_classes = inspect.getmembers(properties, inspect.isclass)
    property_classes = [cls for name, cls in all_properties_classes if issubclass(cls, bpy.types.PropertyGroup)]
    property_classes.reverse()
    for property_class in property_classes:
        bpy.utils.unregister_class(property_class)

    all_operator_classes = inspect.getmembers(operators, inspect.isclass)
    operator_classes = [cls for name, cls in all_operator_classes if issubclass(cls, bpy.types.Operator)]
    operator_classes.reverse()
    for operator_class in operator_classes:
        bpy.utils.unregister_class(operator_class)

    all_panel_classes = inspect.getmembers(panels, inspect.isclass)
    panel_classes = [cls for name, cls in all_panel_classes if issubclass(cls, bpy.types.Panel)]
    panel_classes.reverse()
    for panel_class in panel_classes:
        bpy.utils.unregister_class(panel_class)

    del bpy.types.Object.procedural_bones


if __name__ == "__main__":
    register()
