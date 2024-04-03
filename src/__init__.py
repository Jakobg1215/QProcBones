
from math import degrees, radians, acos
import bpy
from bpy.types import Context, Event, Panel, UIList, UILayout, PropertyGroup, Operator, Pose, PoseBone
from bpy.utils import register_class, unregister_class
from bpy.props import IntProperty, PointerProperty, CollectionProperty, StringProperty, BoolProperty, FloatProperty, FloatVectorProperty
from mathutils import Matrix, Euler, Vector, Quaternion


bl_info = {
    "name": "Quaternion Procedural Bones",
    "description": "A pannel that helps create procedural bones for source engine models.",
    "author": "Jakobg1215",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > QProcBones",
    "tracker_url": "https://github.com/Jakobg1215/qprocbones/issues",
    "category": "Rigging"
}


class QuaternionTrigger(PropertyGroup):
    show_trigger: BoolProperty(default=True)
    tolerance: FloatProperty(default=90, soft_min=0, soft_max=90, precision=6, step=10)
    trigger: FloatVectorProperty(precision=6)
    translation: FloatVectorProperty(precision=6)
    rotation: FloatVectorProperty(precision=6)


class QuaternionProceduralBone(PropertyGroup):
    target_bone: StringProperty()
    control_bone: StringProperty()
    reveal_triggers: BoolProperty()
    triggers: CollectionProperty(type=QuaternionTrigger)
    selected_trigger: IntProperty()


class ProceduralBoneData(PropertyGroup):
    quaternion_procedurals: CollectionProperty(type=QuaternionProceduralBone)
    selected_quaternion_procedural: IntProperty()


class QuaternionTriggerList(UIList):
    bl_idname = "VIEW_3D_UL_QuaternionTriggerList"

    def draw_item(self, context: Context, layout: UILayout, data: QuaternionProceduralBone, item: QuaternionTrigger,
                  icon: int, active_data: QuaternionProceduralBone) -> None:
        col: UILayout = layout.column(align=True)

        row: UILayout = col.row(align=True)
        row.prop(item, "show_trigger", icon="TRIA_DOWN" if item.show_trigger else "TRIA_RIGHT", emboss=False,
                 icon_only=True)
        row.label(text="Trigger")

        if item.show_trigger:
            box: UILayout = col.box()
            col: UILayout = box.column(align=True)

            row: UILayout = col.row(align=True)
            row.prop(item, "tolerance", text="Tolerance")

            row: UILayout = col.row(align=True)
            row.prop(item, "trigger", text="Trigger")
            row.operator("qprocbones.set_trigger_to_current", text="Set")

            row: UILayout = col.row(align=True)
            row.prop(item, "rotation", text="Rotation")
            row.operator("qprocbones.set_rotation_to_current", text="Set")

            row: UILayout = col.row(align=True)
            row.prop(item, "translation", text="Translation")
            row.operator("qprocbones.set_translation_to_current", text="Set")

            col.operator("qprocbones.preview_current_trigger", text="Preview")


class QuaternionProceduralBonesList(UIList):
    bl_idname = "VIEW_3D_UL_QuaternionProceduralBonesList"

    def draw_item(self, context: Context, layout: UILayout, data: ProceduralBoneData, item: QuaternionProceduralBone,
                  icon: int, active_data: ProceduralBoneData) -> None:
        col: UILayout = layout.column(align=True)

        skeleton_pose: Pose = context.scene.procedural_skeleton_target.pose
        row: UILayout = col.row(align=True)
        row.prop_search(item, "target_bone", skeleton_pose, "bones", text="Target")
        row.prop_search(item, "control_bone", skeleton_pose, "bones", text="Control")

        row: UILayout = col.row(align=True)
        row.prop(item, "reveal_triggers", text="Triggers",
                 icon="TRIA_DOWN" if item.reveal_triggers else "TRIA_RIGHT", emboss=False)

        if item.reveal_triggers:
            row: UILayout = col.row(align=True)
            row.template_list("VIEW_3D_UL_QuaternionTriggerList", "", item, "triggers", item, "selected_trigger")

            row: UILayout = row.column(align=True)
            row.operator("qprocbones.add_quaternion_trigger", icon='ADD', text="")
            row.operator("qprocbones.remove_quaternion_trigger", icon='REMOVE', text="")

            row: UILayout = row.column(align=True)
            row.operator("qprocbones.move_quaternion_trigger_up", icon='TRIA_UP', text="")
            row.operator("qprocbones.move_quaternion_trigger_down", icon='TRIA_DOWN', text="")

        row: UILayout = col.row(align=True)
        row.operator("qprocbones.preview_quaternion_procedural", text="Preview")
        row.operator("qprocbones.copy_quaternion_procedural", text="Copy")


class QuaternionProceduralBonesPanel(Panel):
    bl_category = "qprocbones"
    bl_description = ""
    bl_idname = "VIEW_3D_PT_QuaternionProceduralBones"
    bl_label = "Quaternion Procedural Bones"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    def draw(self, context: Context) -> None:
        col: UILayout = self.layout.column(align=True)
        col.prop(context.scene, "procedural_skeleton_target", text="", icon="OUTLINER_OB_ARMATURE")

        if context.scene.procedural_skeleton_target is None:
            return

        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints

        row = col.row(align=True)
        row.template_list("VIEW_3D_UL_QuaternionProceduralBonesList", "", constraints, "quaternion_procedurals",
                          constraints, "selected_quaternion_procedural")

        col: UILayout = row.column(align=True)
        col.operator("qprocbones.add_quaternion_procedural", icon='ADD', text="")
        col.operator("qprocbones.remove_quaternion_procedural", icon='REMOVE', text="")


class AddQuaternionProceduralBone(Operator):
    bl_idname = "qprocbones.add_quaternion_procedural"
    bl_label = "Add Quaternion Procedural Bone"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        constraints.quaternion_procedurals.add()
        constraints.selected_quaternion_procedural = len(constraints.quaternion_procedurals) - 1
        return {'FINISHED'}


class RemoveQuaternionProceduralBone(Operator):
    bl_idname = "qprocbones.remove_quaternion_procedural"
    bl_label = "Remove Quaternion Procedural Bone"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        constraints.quaternion_procedurals.remove(constraints.selected_quaternion_procedural)
        return {'FINISHED'}


class PreviewQuaternionProceduralBone(Operator):
    bl_idname = "qprocbones.preview_quaternion_procedural"
    bl_label = "Preview Quaternion Procedural Bone"

    @classmethod
    def poll(self, context: Context) -> bool:
        return False

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]
        current_pose: Pose = context.scene.procedural_skeleton_target.pose
        control_bone: PoseBone = current_pose.bones[quaternion_procedural.control_bone]

        parent_inverse: Matrix = control_bone.parent.bone.matrix_local.inverted_safe()
        current_rotation: Quaternion = (parent_inverse @ control_bone.bone.matrix_local @
                                        control_bone.matrix_basis).to_quaternion()

        weights = [i for i in range(32)]
        scale = 0

        for index, trigger in enumerate(quaternion_procedural.triggers):
            trigger_rotation = Euler([radians(d) for d in trigger.trigger]).to_quaternion()
            dot: float = abs(trigger_rotation.dot(current_rotation))
            dot = max(-1, min(dot, 1))
            weights[index] = 1 - (2 * acos(dot) * (1 / trigger.tolerance))
            weights[index] = max(0, weights[index])
            scale += weights[index]

        scale = 1.0 / scale

        return {'FINISHED'}


class CopyQuaternionProceduralBone(Operator):
    bl_idname = "qprocbones.copy_quaternion_procedural"
    bl_label = "Copy Quaternion Procedural"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]

        current_pose: Pose = context.scene.procedural_skeleton_target.pose
        control_bone: PoseBone = current_pose.bones[quaternion_procedural.control_bone]
        target_bone: PoseBone = current_pose.bones[quaternion_procedural.target_bone]

        def get_string_after_dot(input_string) -> str:
            parts = input_string.split('.')
            if len(parts) > 1:
                return parts[1]
            else:
                return input_string

        helper_string = "<helper> " + get_string_after_dot(quaternion_procedural.control_bone) + " " + \
                        get_string_after_dot(control_bone.parent.name) + " " + \
                        get_string_after_dot(target_bone.parent.name) + " " + \
                        get_string_after_dot(quaternion_procedural.target_bone) + "\n"

        parent_inverse: Matrix = target_bone.parent.bone.matrix_local.inverted_safe()
        current_position: Vector = (parent_inverse @ target_bone.bone.matrix_local).translation

        base_pos = "<basepos> " + " ".join([str(d) for d in current_position]) + "\n"

        triggers = ""

        for trigger in quaternion_procedural.triggers:
            triggers += "<trigger> " + str(trigger.tolerance) + " " + \
                        " ".join([str(d) for d in trigger.trigger]) + " " + \
                        " ".join([str(d) for d in trigger.rotation]) + " " + \
                        " ".join([str(d) for d in trigger.translation]) + "\n"

        context.window_manager.clipboard = helper_string + base_pos + triggers

        return {'FINISHED'}


class AddQuaternionTrigger(Operator):
    bl_idname = "qprocbones.add_quaternion_trigger"
    bl_label = "Add Quaternion Trigger"

    @classmethod
    def poll(cls, context: Context) -> bool:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]
        return len(quaternion_procedural.triggers) < 32

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]
        quaternion_procedural.triggers.add()
        quaternion_procedural.selected_trigger = len(quaternion_procedural.triggers) - 1
        return {'FINISHED'}


class RemoveQuaternionTrigger(Operator):
    bl_idname = "qprocbones.remove_quaternion_trigger"
    bl_label = "Remove Quaternion Trigger"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]
        quaternion_procedural.triggers.remove(quaternion_procedural.selected_trigger)
        return {'FINISHED'}


class MoveQuaternionTriggerUp(Operator):
    bl_idname = "qprocbones.move_quaternion_trigger_up"
    bl_label = "Move Quaternion Trigger Up"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]
        triggers = quaternion_procedural.triggers
        index = quaternion_procedural.selected_trigger
        if index > 0:
            triggers.move(index, index - 1)
            quaternion_procedural.selected_trigger = index - 1
        return {'FINISHED'}


class MoveQuaternionTriggerDown(Operator):
    bl_idname = "qprocbones.move_quaternion_trigger_down"
    bl_label = "Move Quaternion Trigger Down"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[
            constraints.selected_quaternion_procedural]
        triggers = quaternion_procedural.triggers
        index = quaternion_procedural.selected_trigger
        if index < len(triggers) - 1:
            triggers.move(index, index + 1)
            quaternion_procedural.selected_trigger = index + 1
        return {'FINISHED'}


class SetTriggerToCurrent(Operator):
    bl_idname = "qprocbones.set_trigger_to_current"
    bl_label = "Set Trigger to Current"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        current_quaternion_index: int = constraints.selected_quaternion_procedural
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[current_quaternion_index]
        current_trigger_index: int = quaternion_procedural.selected_trigger
        current_trigger: QuaternionTrigger = quaternion_procedural.triggers[current_trigger_index]
        current_pose: Pose = context.scene.procedural_skeleton_target.pose
        control_bone: PoseBone = current_pose.bones[quaternion_procedural.control_bone]

        parent_inverse: Matrix = control_bone.parent.bone.matrix_local.inverted_safe()
        current_rotation: Matrix = parent_inverse @ control_bone.bone.matrix_local @ control_bone.matrix_basis

        rotation = [degrees(d) for d in current_rotation.to_euler()]

        current_trigger.trigger = rotation

        return {'FINISHED'}


class SetTranslationToCurrent(Operator):
    bl_idname = "qprocbones.set_translation_to_current"
    bl_label = "Set Translation to Current"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        current_quaternion_index: int = constraints.selected_quaternion_procedural
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[current_quaternion_index]
        current_trigger_index: int = quaternion_procedural.selected_trigger
        current_trigger: QuaternionTrigger = quaternion_procedural.triggers[current_trigger_index]
        current_pose: Pose = context.scene.procedural_skeleton_target.pose
        target_bone: PoseBone = current_pose.bones[quaternion_procedural.target_bone]

        current_trigger.translation = target_bone.matrix_basis.to_translation()

        return {'FINISHED'}


class SetRotationToCurrent(Operator):
    bl_idname = "qprocbones.set_rotation_to_current"
    bl_label = "Set Rotation to Current"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == 'POSE'

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        current_quaternion_index: int = constraints.selected_quaternion_procedural
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[current_quaternion_index]
        current_trigger_index: int = quaternion_procedural.selected_trigger
        current_trigger: QuaternionTrigger = quaternion_procedural.triggers[current_trigger_index]
        current_pose: Pose = context.scene.procedural_skeleton_target.pose
        target_bone: PoseBone = current_pose.bones[quaternion_procedural.target_bone]

        parent_inverse: Matrix = target_bone.parent.bone.matrix_local.inverted_safe()
        current_rotation: Matrix = parent_inverse @ target_bone.bone.matrix_local @ target_bone.matrix_basis

        rotation = [degrees(d) for d in current_rotation.to_euler()]

        current_trigger.rotation = rotation

        return {'FINISHED'}


class PreviewQuaternionTrigger(Operator):
    bl_idname = "qprocbones.preview_current_trigger"
    bl_label = "Preview Current Trigger"

    def execute(self, context: Context) -> set:
        constraints: ProceduralBoneData = context.scene.procedural_skeleton_target.procedural_skeleton_constraints
        current_quaternion_index: int = constraints.selected_quaternion_procedural
        quaternion_procedural: QuaternionProceduralBone = constraints.quaternion_procedurals[current_quaternion_index]
        current_trigger_index: int = quaternion_procedural.selected_trigger
        current_trigger: QuaternionTrigger = quaternion_procedural.triggers[current_trigger_index]
        current_pose: Pose = context.scene.procedural_skeleton_target.pose
        control_bone: PoseBone = current_pose.bones[quaternion_procedural.control_bone]
        target_bone: PoseBone = current_pose.bones[quaternion_procedural.target_bone]

        control_bone_target_rotation = Euler([radians(d) for d in current_trigger.trigger]).to_quaternion()
        control_bone_parent_offset = (control_bone.parent.bone.matrix_local.inverted_safe()
                                      @ control_bone.bone.matrix_local).to_quaternion()
        control_bone_target_difference = control_bone_target_rotation.rotation_difference(
            control_bone_parent_offset).to_matrix().to_4x4().inverted_safe()
        control_bone.matrix_basis = control_bone_target_difference
        # FIXME: Make this so it only effects rotation and not location and scale.

        target_bone_target_rotation = Euler([radians(d) for d in current_trigger.rotation]).to_quaternion()
        target_bone_parent_offset = (target_bone.parent.bone.matrix_local.inverted_safe()
                                     @ target_bone.bone.matrix_local).to_quaternion()
        target_bone_target_difference = target_bone_target_rotation.rotation_difference(
            target_bone_parent_offset).to_matrix().to_4x4().inverted_safe()
        target_bone.matrix_basis = target_bone_target_difference
        target_bone.matrix_basis.translation = current_trigger.translation

        return {'FINISHED'}


def register() -> None:
    register_class(QuaternionProceduralBonesList)
    register_class(QuaternionProceduralBonesPanel)
    register_class(AddQuaternionProceduralBone)
    register_class(RemoveQuaternionProceduralBone)
    register_class(QuaternionTrigger)
    register_class(QuaternionProceduralBone)
    register_class(ProceduralBoneData)
    register_class(QuaternionTriggerList)
    register_class(PreviewQuaternionProceduralBone)
    register_class(CopyQuaternionProceduralBone)
    register_class(AddQuaternionTrigger)
    register_class(RemoveQuaternionTrigger)
    register_class(MoveQuaternionTriggerUp)
    register_class(MoveQuaternionTriggerDown)
    register_class(SetTriggerToCurrent)
    register_class(SetTranslationToCurrent)
    register_class(SetRotationToCurrent)
    register_class(PreviewQuaternionTrigger)

    bpy.types.Scene.procedural_skeleton_target = PointerProperty(
        type=bpy.types.Object,
        poll=lambda self, object: object.type == 'ARMATURE',
    )

    bpy.types.Object.procedural_skeleton_constraints = PointerProperty(type=ProceduralBoneData)


def unregister() -> None:
    unregister_class(QuaternionProceduralBonesList)
    unregister_class(QuaternionProceduralBonesPanel)
    unregister_class(AddQuaternionProceduralBone)
    unregister_class(RemoveQuaternionProceduralBone)
    unregister_class(QuaternionTrigger)
    unregister_class(QuaternionProceduralBone)
    unregister_class(ProceduralBoneData)
    unregister_class(QuaternionTriggerList)
    unregister_class(PreviewQuaternionProceduralBone)
    unregister_class(CopyQuaternionProceduralBone)
    unregister_class(AddQuaternionTrigger)
    unregister_class(RemoveQuaternionTrigger)
    unregister_class(MoveQuaternionTriggerUp)
    unregister_class(MoveQuaternionTriggerDown)
    unregister_class(SetTriggerToCurrent)
    unregister_class(SetTranslationToCurrent)
    unregister_class(SetRotationToCurrent)
    unregister_class(PreviewQuaternionTrigger)

    del bpy.types.Scene.procedural_skeleton_target
    del bpy.types.Object.procedural_skeleton_constraints


if __name__ == "__main__":
    register()
