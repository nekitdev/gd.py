from gd.memory.arrays import MutArrayData
from gd.memory.base import Struct, StructData, struct
from gd.memory.data import (
    Bool,
    Float,
    Int,
    UByte,
    UInt,
)
from gd.memory.fields import Field
from gd.memory.pointers import MutPointerData
from gd.memory.special import Void


@struct()
class CCPoint(Struct):
    x = Field(Float())
    y = Field(Float())


@struct()
class CCSize(Struct):
    width = Field(Float())
    height = Field(Float())


@struct()
class CCAffineTransform(Struct):
    a = Field(Float())
    b = Field(Float())
    c = Field(Float())
    d = Field(Float())
    translate_x = Field(Float())
    translate_y = Field(Float())


@struct()
class ColorRGB(Struct):
    r = Field(UByte())
    g = Field(UByte())
    b = Field(UByte())


@struct(virtual=True)
class CCCopying(Struct):
    pass


@struct()
class CCObject(CCCopying):
    id = Field(UInt())
    ref_id = Field(Int())

    tag = Field(UInt())  # modified

    ref_count = Field(UInt())
    auto_release_count = Field(UInt())

    object_type = Field(Int())  # enum  # modified
    index_in_array = Field(UInt())


@struct()
class CCArrayStruct(Struct):
    length = Field(UInt())
    capacity = Field(UInt())
    # this is actually CCObject double pointer,
    # but since we do not have indexing or iterating pointers implemented,
    # we instead make it point to an array of pointers
    array = Field(MutPointerData(MutArrayData(MutPointerData(StructData(CCObject)))))


@struct()
class CCArray(CCObject):
    data = Field(MutPointerData(StructData(CCArrayStruct)))


@struct(virtual=True)
class CCNode(CCObject):
    rotation_x = Field(Float())
    rotation_y = Field(Float())
    scale_x = Field(Float())
    scale_y = Field(Float())

    vertex_z = Field(Float())

    position = Field(StructData(CCPoint))

    skew_x = Field(Float())
    skew_y = Field(Float())

    anchor_in_points = Field(StructData(CCPoint))
    anchor = Field(StructData(CCPoint))

    content_size = Field(StructData(CCSize))

    additional_transform = Field(StructData(CCAffineTransform))
    transform = Field(StructData(CCAffineTransform))
    inverse = Field(StructData(CCAffineTransform))

    camera = Field(MutPointerData(Void()))  # CCCamera*

    grid = Field(MutPointerData(Void()))  # CCGridBase*

    z_order = Field(Int())

    children = Field(MutPointerData(StructData(CCArray)))

    parent = Field(MutPointerData(Void()))  # CCNode*

    user_data = Field(MutPointerData(Void()))  # void*
    user_object = Field(MutPointerData(StructData(CCObject)))

    shader_program = Field(MutPointerData(Void()))  # CCGLProgram*

    server_state = Field(Int())  # enum

    order_of_arrival = Field(UInt())

    scheduler = Field(MutPointerData(Void()))  # CCScheduler*

    action_manager = Field(MutPointerData(Void()))  # CCActionManager*

    running = Field(Bool())

    transform_dirty = Field(Bool())
    inverse_dirty = Field(Bool())
    additional_transform_dirty = Field(Bool())
    visible = Field(Bool())

    ignore_anchor_point_for_position = Field(Bool())

    reorder_child_dirty = Field(Bool())

    script_handler = Field(Int())
    update_script_handler = Field(Int())
    script_type = Field(Int())  # enum

    component_container = Field(MutPointerData(Void()))  # CCComponentContainer*


@struct(virtual=True)
class CCNodeRGBA(CCNode):
    displayed_opacity = Field(UByte())
    real_opacity = Field(UByte())

    displayed_color = Field(StructData(ColorRGB))
    real_color = Field(StructData(ColorRGB))

    cascade_color_enabled = Field(Bool())
    cascade_opacity_enabled = Field(Bool())


@struct(virtual=True)
class CCTouchDelegate(Struct):
    pass


@struct(virtual=True)
class CCAccelerometerDelegate(Struct):
    pass


@struct(virtual=True)
class CCKeypadDelegate(Struct):
    pass


@struct(virtual=True)
class CCKeyboardDelegate(Struct):
    pass


@struct(virtual=True)
class CCMouseDelegate(Struct):
    pass


@struct(virtual=True)
class CCLayer(
    CCMouseDelegate,
    CCKeyboardDelegate,
    CCKeypadDelegate,
    CCAccelerometerDelegate,
    CCTouchDelegate,
    CCNode,
):
    touch_enabled = Field(Bool())
    accelerometer_enabled = Field(Bool())
    keypad_enabled = Field(Bool())
    keyboard_enabled = Field(Bool())
    mouse_enabled = Field(Bool())

    script_touch_handler_entry = Field(MutPointerData(Void()))  # CCTouchScriptHandlerEntry*
    script_keypad_handler_entry = Field(MutPointerData(Void()))  # CCScriptHandlerEntry*
    script_accelerometer_handler_entry = Field(MutPointerData(Void()))  # CCScriptHandlerEntry*

    touch_priority = Field(Int())
    touch_mode = Field(Int())  # enum
