
import bpy


class QuaternionProceduralBonesPanel(bpy.types.Panel):
    bl_category = "qprocbones"
    bl_idname = "VIEW_3D_PT_QuaternionProceduralBones"
    bl_label = "Quaternion Procedural Bones"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.object and context.object.type == 'ARMATURE'

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        armature = context.object
        procedural_bones = armature.procedural_bones

        col = layout.column(align=True)
        col.operator("qprocbones.add_quaternion_procedural")

        if not len(procedural_bones.quaternion_bones):
            return

        box = col.box()

        for procedural_index, quaternion_procedural in enumerate(procedural_bones.quaternion_bones):
            procedural_col = box.column(align=True)
            procedural_name = quaternion_procedural.target_bone + " - " + quaternion_procedural.control_bone \
                if quaternion_procedural.target_bone and quaternion_procedural.control_bone \
                else "Quaternion Procedural"
            procedural_col.prop(quaternion_procedural, "reveal", text=procedural_name,
                                icon="TRIA_DOWN" if quaternion_procedural.reveal else "TRIA_RIGHT")

            if not quaternion_procedural.reveal:
                continue

            procedural_box = procedural_col.box()
            procedural_col = procedural_box.column(align=True)
            procedural_col.prop_search(quaternion_procedural, "target_bone", armature.pose, "bones", text="Target Bone")
            procedural_col.prop_search(quaternion_procedural, "control_bone", armature.pose, "bones", 
                                       text="Control Bone")
            
            if not valid_selected_procedural_bones(armature.pose.bones, quaternion_procedural.target_bone, quaternion_procedural.control_bone):
                procedural_col = procedural_box.column(align=True)
                remove_procedural = procedural_col.operator("qprocbones.remove_quaternion_procedural", text="Remove")
                remove_procedural.procedural_index = procedural_index
                continue

            procedural_col = procedural_box.column(align=True)
            add_trigger = procedural_col.operator("qprocbones.add_trigger")
            add_trigger.procedural_index = procedural_index

            procedural_col = procedural_box.column(align=True)
            procedural_col.prop(quaternion_procedural, "reveal_triggers", text="Triggers",
                                icon="TRIA_DOWN" if quaternion_procedural.reveal_triggers else "TRIA_RIGHT")
            if quaternion_procedural.reveal_triggers:
                for trigger_index, trigger in enumerate(quaternion_procedural.triggers):
                    trigger_box = procedural_col.box()
                    trigger_col = trigger_box.column(align=True)
                    trigger_name = trigger.name if trigger.name else "Trigger"
                    trigger_col.prop(trigger, "reveal", text=trigger_name,
                                     icon="TRIA_DOWN" if trigger.reveal else "TRIA_RIGHT")

                    if not trigger.reveal:
                        continue

                    trigger_col = trigger_box.column(align=True)
                    trigger_col.prop(trigger, "name", text="Name")

                    trigger_col = trigger_box.column(align=True)
                    trigger_col.prop(trigger, "tolerance", text="Tolerance")

                    trigger_row = trigger_col.row(align=True)
                    trigger_row.prop(trigger, "trigger_angle", text="Trigger")
                    trigger_set = trigger_row.operator("qprocbones.set_trigger_angle", text="Set")
                    trigger_set.procedural_index = procedural_index
                    trigger_set.trigger_index = trigger_index

                    trigger_row = trigger_col.row(align=True)
                    trigger_row.prop(trigger, "target_angle", text="Angle")
                    trigger_set = trigger_row.operator("qprocbones.set_target_angle", text="Set")
                    trigger_set.procedural_index = procedural_index
                    trigger_set.trigger_index = trigger_index

                    trigger_row = trigger_col.row(align=True)
                    trigger_row.prop(trigger, "target_position", text="Position")
                    trigger_set = trigger_row.operator("qprocbones.set_target_position", text="Set")
                    trigger_set.procedural_index = procedural_index
                    trigger_set.trigger_index = trigger_index

                    preview_trigger = trigger_col.operator("qprocbones.preview_trigger", text="Preview")
                    preview_trigger.procedural_index = procedural_index
                    preview_trigger.trigger_index = trigger_index
                    
                    trigger_col = trigger_box.column(align=True)
                    remove_trigger = trigger_col.operator("qprocbones.remove_trigger", text="Remove")
                    remove_trigger.procedural_index = procedural_index
                    remove_trigger.trigger_index = trigger_index

            procedural_col = procedural_box.column(align=True)
            procedural_row = procedural_col.row(align=True)
            preview_procedural = procedural_row.operator("qprocbones.preview_quaternion_procedural", text="Preview",
                                                         icon="PLAY" if quaternion_procedural.previewing else "PAUSE")
            preview_procedural.procedural_index = procedural_index

            copy_procedural = procedural_row.operator("qprocbones.copy_quaternion_procedural", text="Copy")
            copy_procedural.procedural_index = procedural_index

            procedural_col = procedural_box.column(align=True)
            remove_procedural = procedural_col.operator("qprocbones.remove_quaternion_procedural", text="Remove")
            remove_procedural.procedural_index = procedural_index
            


def valid_selected_procedural_bones(bones: list[bpy.types.PoseBone], target: str, control: str) -> bool:
    if not target:
        return False

    if not control:
        return False

    if target == control:
        return False
    
    target_bone = bones[target]

    if target_bone.parent is None:
        return False
    
    control_bone = bones[control]

    if control_bone.parent is None:
        return False

    return True