# type: ignore

from typing_extensions import TypeAlias

from gd.memory.fields import mut_field
from gd.memory.markers import (
    Struct,
    bool_t,
    float_t,
    int_t,
    mut_array,
    mut_pointer,
    this,
    ubyte_t,
    uint_t,
    void,
)


class CCPoint(Struct):
    x: float_t = mut_field()
    y: float_t = mut_field()


class CCSize(Struct):
    width: float_t = mut_field()
    height: float_t = mut_field()


class CCRectangle(Struct):
    origin: CCPoint = mut_field()
    size: CCSize = mut_field()


class CCAffineTransform(Struct):
    a: float_t = mut_field()
    b: float_t = mut_field()
    c: float_t = mut_field()
    d: float_t = mut_field()
    translate_x: float_t = mut_field()
    translate_y: float_t = mut_field()


class ColorRGB(Struct):
    r: ubyte_t = mut_field()
    g: ubyte_t = mut_field()
    b: ubyte_t = mut_field()


class CCCopying(Struct, vtable=True):
    pass


class CCObject(CCCopying):
    id: uint_t = mut_field()
    ref_id: int_t = mut_field()

    tag: uint_t = mut_field()  # modified
    object_type: int_t = mut_field()  # enum  # modified

    ref_count: uint_t = mut_field()
    auto_release_count: uint_t = mut_field()

    padding: uint_t = mut_field()  # modified


array_mut_pointer: TypeAlias = mut_pointer(mut_array(mut_pointer(CCObject)))


class CCArrayStruct(Struct):
    length: uint_t = mut_field()
    capacity: uint_t = mut_field()
    # this is actually CCObject double pointer,
    # but since we do not have indexing or iterating pointers implemented,
    # we instead make it point to an array of pointers
    array: array_mut_pointer = mut_field()


array_struct_pointer: TypeAlias = mut_pointer(CCArrayStruct)


class CCArray(CCObject):
    data: array_struct_pointer = mut_field()


void_mut_pointer: TypeAlias = mut_pointer(void)
this_mut_pointer: TypeAlias = mut_pointer(this)
cc_array_mut_pointer: TypeAlias = mut_pointer(CCArray)
cc_object_mut_pointer: TypeAlias = mut_pointer(CCObject)


class CCNode(CCObject, vtable=True):
    rotation_x: float_t = mut_field()
    rotation_y: float_t = mut_field()
    scale_x: float_t = mut_field()
    scale_y: float_t = mut_field()

    vertex_z: float_t = mut_field()

    position: CCPoint = mut_field()

    skew_x: float_t = mut_field()
    skew_y: float_t = mut_field()

    anchor_in_points: CCPoint = mut_field()
    anchor: CCPoint = mut_field()

    content_size: CCSize = mut_field()

    additional_transform: CCAffineTransform = mut_field()
    transform: CCAffineTransform = mut_field()
    inverse: CCAffineTransform = mut_field()

    camera: void_mut_pointer = mut_field()  # CCCamera*

    grid: void_mut_pointer = mut_field()  # CCGridBase*

    z_order: int_t = mut_field()

    children: cc_array_mut_pointer = mut_field()

    parent: this_mut_pointer = mut_field()

    user_data: void_mut_pointer = mut_field()  # void
    user_object: cc_object_mut_pointer = mut_field()

    shader_program: void_mut_pointer = mut_field()  # CCGLProgram

    server_state: int_t = mut_field()  # enum

    order_of_arrival: uint_t = mut_field()

    scheduler: void_mut_pointer = mut_field()  # CCScheduler

    action_manager: void_mut_pointer = mut_field()  # CCActionManager

    running: bool_t = mut_field()

    transform_dirty: bool_t = mut_field()
    inverse_dirty: bool_t = mut_field()
    additional_transform_dirty: bool_t = mut_field()
    visible: bool_t = mut_field()

    ignore_anchor_point_for_position: bool_t = mut_field()

    reorder_child_dirty: bool_t = mut_field()

    script_handler: int_t = mut_field()
    update_script_handler: int_t = mut_field()
    script_type: int_t = mut_field()  # enum

    component_container: void_mut_pointer = mut_field()  # CCComponentContainer


class CCNodeRGBA(CCNode, vtable=True):
    displayed_opacity: ubyte_t = mut_field()
    real_opacity: ubyte_t = mut_field()

    displayed_color: ColorRGB = mut_field()
    real_color: ColorRGB = mut_field()

    cascade_color_enabled: bool_t = mut_field()
    cascade_opacity_enabled: bool_t = mut_field()


class CCTouchDelegate(Struct, vtable=True):
    pass


class CCAccelerometerDelegate(Struct, vtable=True):
    pass


class CCKeypadDelegate(Struct, vtable=True):
    pass


class CCKeyboardDelegate(Struct, vtable=True):
    pass


class CCMouseDelegate(Struct, vtable=True):
    pass


class CCLayer(
    CCMouseDelegate,
    CCKeyboardDelegate,
    CCKeypadDelegate,
    CCAccelerometerDelegate,
    CCTouchDelegate,
    CCNode,
    vtable=True,
):
    touch_enabled: bool_t = mut_field()
    accelerometer_enabled: bool_t = mut_field()
    keypad_enabled: bool_t = mut_field()
    keyboard_enabled: bool_t = mut_field()
    mouse_enabled: bool_t = mut_field()

    script_touch_handler_entry: void_mut_pointer = mut_field()  # CCTouchScriptHandlerEntry
    script_keypad_handler_entry: void_mut_pointer = mut_field()  # CCScriptHandlerEntry
    script_accelerometer_handler_entry: void_mut_pointer = mut_field()  # CCScriptHandlerEntry

    touch_priority: int_t = mut_field()
    touch_mode: int_t = mut_field()  # enum
