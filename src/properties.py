
import bpy


class QuaternionProceduralTriggerProperty(bpy.types.PropertyGroup):
    reveal: bpy.props.BoolProperty(default=True, description="Show or hide the trigger data")
    name: bpy.props.StringProperty(description="The name of the trigger")
    tolerance: bpy.props.FloatProperty(default=90, soft_min=0, soft_max=90, description="The tolerance for the trigger")
    trigger_angle: bpy.props.FloatVectorProperty(precision=6, description="The angle that will trigger the procedural")
    target_angle: bpy.props.FloatVectorProperty(
        precision=6, description="The angle that the procedural will set the target bone to")
    target_position: bpy.props.FloatVectorProperty(
        precision=6, description="The position that the procedural will set the target bone to")


class QuaternionProceduralProperty(bpy.types.PropertyGroup):
    reveal: bpy.props.BoolProperty(default=True, description="Show or hide the procedural data")
    target_bone: bpy.props.StringProperty(description="The bone that will be affected by the procedural")
    control_bone: bpy.props.StringProperty(description="The bone that will drive the procedural")
    reveal_triggers: bpy.props.BoolProperty(default=True, description="Show or hide the triggers")
    triggers: bpy.props.CollectionProperty(type=QuaternionProceduralTriggerProperty)
    previewing: bpy.props.BoolProperty()


class ProceduralBonesDataProperty(bpy.types.PropertyGroup):
    quaternion_bones: bpy.props.CollectionProperty(type=QuaternionProceduralProperty)
