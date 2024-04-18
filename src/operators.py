
from math import degrees, radians, acos
from typing import Set
from mathutils import Euler, Quaternion, Vector
import bpy


# region Quaternion Triggers

class SetQuaternionTargetPosition(bpy.types.Operator):
    bl_idname = "qprocbones.set_target_position"
    bl_label = "Set Target Position"
    bl_description = "Set the target position to the current position of the control bone"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()
    trigger_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        bones = armature.pose.bones
        target_bone = bones[quaternion_bone.target_bone]
        trigger = quaternion_bone.triggers[self.trigger_index]

        trigger.target_position = target_bone.matrix_basis.to_translation()
        return {'FINISHED'}


class SetQuaternionTargetAngle(bpy.types.Operator):
    bl_idname = "qprocbones.set_target_angle"
    bl_label = "Set Target Angle"
    bl_description = "Set the target angle to the current angle of the control bone"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()
    trigger_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        bones = armature.pose.bones
        target_bone = bones[quaternion_bone.target_bone]
        trigger = quaternion_bone.triggers[self.trigger_index]

        parent_inverse = target_bone.parent.bone.matrix_local.inverted_safe()
        current_rotation = parent_inverse @ target_bone.bone.matrix_local @ target_bone.matrix_basis

        rotation = [degrees(d) for d in current_rotation.to_euler()]
        trigger.target_angle = rotation
        return {'FINISHED'}


class SetQuaternionTriggerAngle(bpy.types.Operator):
    bl_idname = "qprocbones.set_trigger_angle"
    bl_label = "Set Trigger Angle"
    bl_description = "Set the trigger angle to the current angle of the control bone"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()
    trigger_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        bones = armature.pose.bones
        control_bone = bones[quaternion_bone.control_bone]
        trigger = quaternion_bone.triggers[self.trigger_index]

        parent_inverse = control_bone.parent.bone.matrix_local.inverted_safe()
        current_rotation = parent_inverse @ control_bone.bone.matrix_local @ control_bone.matrix_basis

        rotation = [degrees(d) for d in current_rotation.to_euler()]
        trigger.trigger_angle = rotation
        return {'FINISHED'}


class PreviewQuaternionTrigger(bpy.types.Operator):
    bl_idname = "qprocbones.preview_trigger"
    bl_label = "Preview Trigger"
    bl_description = "Set the trigger and control bone to the trigger values"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()
    trigger_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        bones = armature.pose.bones
        target_bone = bones[quaternion_bone.target_bone]
        control_bone = bones[quaternion_bone.control_bone]
        trigger = quaternion_bone.triggers[self.trigger_index]

        control_bone_target_rotation = Euler([radians(d) for d in trigger.trigger_angle]).to_quaternion()
        control_bone_parent_offset = (control_bone.parent.bone.matrix_local.inverted_safe()
                                      @ control_bone.bone.matrix_local).to_quaternion()
        control_bone_target_difference = control_bone_target_rotation.rotation_difference(
            control_bone_parent_offset).to_matrix().to_4x4().inverted_safe()
        control_bone.matrix_basis = control_bone_target_difference
        # FIXME: Make this so it only effects rotation and not location and scale.

        target_bone_target_rotation = Euler([radians(d) for d in trigger.target_angle]).to_quaternion()
        target_bone_parent_offset = (target_bone.parent.bone.matrix_local.inverted_safe()
                                     @ target_bone.bone.matrix_local).to_quaternion()
        target_bone_target_difference = target_bone_target_rotation.rotation_difference(
            target_bone_parent_offset).to_matrix().to_4x4().inverted_safe()
        target_bone.matrix_basis = target_bone_target_difference
        target_bone.matrix_basis.translation = trigger.target_position

        return {'FINISHED'}


class RemoveQuaternionTrigger(bpy.types.Operator):
    bl_idname = "qprocbones.remove_trigger"
    bl_label = "Remove Trigger"
    bl_description = "Remove the selected trigger from the list"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()
    trigger_index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        quaternion_bone.triggers.remove(self.trigger_index)
        return {'FINISHED'}


class AddQuaternionTrigger(bpy.types.Operator):
    bl_idname = "qprocbones.add_trigger"
    bl_label = "Add Trigger"
    bl_description = "Add a new trigger to the list"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]

        if len(quaternion_bone.triggers) >= 32:
            self.report({'ERROR'}, "Quaternion Procedural Can't Have More Than 32 Triggers!")
            return {'FINISHED'}

        quaternion_bone.triggers.add()
        return {'FINISHED'}

# endregion

# region Quaternion Procedurals


class CopyQuaternionProcedural(bpy.types.Operator):
    bl_idname = "qprocbones.copy_quaternion_procedural"
    bl_label = "Copy Procedural"
    bl_description = "Copy the selected procedural bone"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        bones = armature.pose.bones
        target_bone = bones[quaternion_bone.target_bone]
        control_bone = bones[quaternion_bone.control_bone]

        def get_string_after_dot(input_string: str) -> str:
            parts = input_string.split('.', 1)
            if len(parts) > 1:
                return parts[1]
            else:
                return input_string

        helper_string = "<helper> " + get_string_after_dot(target_bone.name) + " " + \
                        get_string_after_dot(target_bone.parent.name) + " " + \
                        get_string_after_dot(control_bone.parent.name) + " " + \
                        get_string_after_dot(control_bone.name) + "\n"

        parent_inverse = target_bone.parent.bone.matrix_local.inverted_safe()
        current_position = (parent_inverse @ target_bone.bone.matrix_local).translation
        base_pos = "<basepos> " + " ".join([str(d) for d in current_position]) + "\n"

        triggers = ""

        for trigger in quaternion_bone.triggers:
            triggers += "<trigger> " + str(trigger.tolerance) + " " + \
                        " ".join([str(d) for d in trigger.trigger_angle]) + " " + \
                        " ".join([str(d) for d in trigger.target_angle]) + " " + \
                        " ".join([str(d) for d in trigger.target_position]) + "\n"

        context.window_manager.clipboard = helper_string + base_pos + triggers
        return {'FINISHED'}


class PreviewQuaternionProcedural(bpy.types.Operator):
    bl_idname = "qprocbones.preview_quaternion_procedural"
    bl_label = "Preview Procedural"
    bl_description = "Preview the procedural bone"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()

    def __init__(self) -> None:
        self.timer = None

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.mode == 'POSE'

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> Set[str]:
        if context.mode != 'POSE':
            self.cancel(context)
            return {'FINISHED'}

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]
        bones = armature.pose.bones
        target_bone = bones[quaternion_bone.target_bone]
        control_bone = bones[quaternion_bone.control_bone]
        triggers = quaternion_bone.triggers

        if not quaternion_bone.previewing:
            self.cancel(context)
            return {'FINISHED'}

        if len(triggers) == 0:
            self.report({'ERROR'}, "Quaternion Procedural Requires At Least One Trigger")
            self.cancel(context)
            return {'CANCELLED'}

        # This is a translation of this function https://github.com/ValveSoftware/source-sdk-2013/blob/master/mp/src/public/bone_setup.cpp#L4703

        control_parent_inverse = control_bone.parent.bone.matrix_local.inverted_safe()
        control_current_rotation = (control_parent_inverse @ control_bone.bone.matrix_local @
                                    control_bone.matrix_basis).to_quaternion()
        weights = [i for i in range(32)]
        scale = 0

        for index, trigger in enumerate(triggers):
            trigger_rotation = Euler([radians(d) for d in trigger.trigger_angle]).to_quaternion()
            dot = abs(trigger_rotation.dot(control_current_rotation))
            dot = max(-1, min(dot, 1))
            weights[index] = 1 - (2 * acos(dot) * (1 / radians(trigger.tolerance)))
            weights[index] = max(0, weights[index])
            scale += weights[index]

        if scale <= 0.001:  # EPSILON?
            target_bone_target_rotation = Euler([radians(d) for d in triggers[0].target_angle]).to_quaternion()
            target_bone_parent_offset = (target_bone.parent.bone.matrix_local.inverted_safe()
                                         @ target_bone.bone.matrix_local).to_quaternion()
            target_bone_target_difference = target_bone_target_rotation.rotation_difference(
                target_bone_parent_offset).to_matrix().to_4x4().inverted_safe()
            target_bone.matrix_basis = target_bone_target_difference
            target_bone.matrix_basis.translation = triggers[0].target_position
            return {'PASS_THROUGH'}

        scale = 1 / scale

        quat = Quaternion((0, 0, 0, 0))
        pos = Vector((0, 0, 0))

        for index, trigger in enumerate(triggers):
            if weights[index] == 0:
                continue

            s = weights[index] * scale

            target_angle = Euler([radians(d) for d in trigger.target_angle]).to_quaternion()
            quat.x = quat.x + s * target_angle.x
            quat.y = quat.y + s * target_angle.y
            quat.z = quat.z + s * target_angle.z
            quat.w = quat.w + s * target_angle.w
            pos[0] = pos[0] + s * trigger.target_position[0]
            pos[1] = pos[1] + s * trigger.target_position[1]
            pos[2] = pos[2] + s * trigger.target_position[2]

        target_bone_parent_offset = (target_bone.parent.bone.matrix_local.inverted_safe()
                                     @ target_bone.bone.matrix_local).to_quaternion()
        target_bone_target_difference = quat.rotation_difference(
            target_bone_parent_offset).to_matrix().to_4x4().inverted_safe()
        target_bone.matrix_basis = target_bone_target_difference
        target_bone.matrix_basis.translation = pos

        return {'PASS_THROUGH'}

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]

        if quaternion_bone.previewing:
            quaternion_bone.previewing = False
        else:
            self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
            quaternion_bone.previewing = True
            return {'RUNNING_MODAL'}

        return {'FINISHED'}

    def cancel(self, context: bpy.types.Context):
        if self.timer is None:
            return

        armature = context.object
        procedural_bones = armature.procedural_bones
        quaternion_bone = procedural_bones.quaternion_bones[self.procedural_index]

        context.window_manager.event_timer_remove(self.timer)
        self.timer = None


class RemoveQuaternionProcedural(bpy.types.Operator):
    bl_idname = "qprocbones.remove_quaternion_procedural"
    bl_label = "Remove Procedural"
    bl_description = "Remove the selected procedural bone from the list"
    bl_options = {'REGISTER'}

    procedural_index: bpy.props.IntProperty()

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        procedural_bones.quaternion_bones.remove(self.procedural_index)
        return {'FINISHED'}


class AddQuaternionProcedural(bpy.types.Operator):
    bl_idname = "qprocbones.add_quaternion_procedural"
    bl_label = "Add Procedural"
    bl_description = "Add a new quaternion procedural bone to the list"
    bl_options = {'REGISTER'}

    def execute(self, context: bpy.types.Context) -> set:
        armature = context.object
        procedural_bones = armature.procedural_bones
        procedural_bones.quaternion_bones.add()
        return {'FINISHED'}

# endregion
