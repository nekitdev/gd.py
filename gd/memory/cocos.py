from typing_extensions import TypeAlias

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
    x: float_t
    y: float_t


class CCSize(Struct):
    width: float_t
    height: float_t


class CCRectangle(Struct):
    point: CCPoint
    size: CCSize


class CCAffineTransform(Struct):
    a: float_t
    b: float_t
    c: float_t
    d: float_t
    translate_x: float_t
    translate_y: float_t


class ColorRGB(Struct):
    r: ubyte_t
    g: ubyte_t
    b: ubyte_t


class CCCopying(Struct, vtable=True):
    pass


class CCObject(CCCopying):
    id: uint_t
    ref_id: int_t

    tag: uint_t  # modified
    object_type: int_t  # enum  # modified

    ref_count: uint_t
    auto_release_count: uint_t

    padding: uint_t  # modified


array_mut_pointer: TypeAlias = mut_pointer(mut_array(mut_pointer(CCObject)))


class CCArrayStruct(Struct):
    length: uint_t
    capacity: uint_t
    # this is actually CCObject double pointer,
    # but since we do not have indexing or iterating pointers implemented,
    # we instead make it point to an array of pointers
    array: array_mut_pointer


array_struct_pointer: TypeAlias = mut_pointer(CCArrayStruct)


class CCArray(CCObject):
    data: array_struct_pointer


void_mut_pointer: TypeAlias = mut_pointer(void)
this_mut_pointer: TypeAlias = mut_pointer(this)
cc_array_mut_pointer: TypeAlias = mut_pointer(CCArray)
cc_object_mut_pointer: TypeAlias = mut_pointer(CCObject)


class CCNode(CCObject, vtable=True):
    rotation_x: float_t
    rotation_y: float_t
    scale_x: float_t
    scale_y: float_t

    vertex_z: float_t

    position: CCPoint

    skew_x: float_t
    skew_y: float_t

    anchor_in_points: CCPoint
    anchor: CCPoint

    content_size: CCSize

    additional_transform: CCAffineTransform
    transform: CCAffineTransform
    inverse: CCAffineTransform

    camera: void_mut_pointer  # CCCamera

    grid: void_mut_pointer  # CCGridBase

    z_order: int_t

    children: cc_array_mut_pointer

    parent: this_mut_pointer

    user_data: void_mut_pointer  # void
    user_object: cc_object_mut_pointer

    shader_program: void_mut_pointer  # CCGLProgram

    server_state: int_t  # enum

    order_of_arrival: uint_t

    scheduler: void_mut_pointer  # CCScheduler

    action_manager: void_mut_pointer  # CCActionManager

    running: bool_t

    transform_dirty: bool_t
    inverse_dirty: bool_t
    additional_transform_dirty: bool_t
    visible: bool_t

    ignore_anchor_point_for_position: bool_t

    reorder_child_dirty: bool_t

    script_handler: int_t
    update_script_handler: int_t
    script_type: int_t  # enum

    component_container: void_mut_pointer  # CCComponentContainer


class CCNodeRGBA(CCNode, vtable=True):
    displayed_opacity: ubyte_t
    real_opacity: ubyte_t

    displayed_color: ColorRGB
    real_color: ColorRGB

    cascade_color_enabled: bool_t
    cascade_opacity_enabled: bool_t


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
    touch_enabled: bool_t
    accelerometer_enabled: bool_t
    keypad_enabled: bool_t
    keyboard_enabled: bool_t
    mouse_enabled: bool_t

    script_touch_handler_entry: void_mut_pointer  # CCTouchScriptHandlerEntry
    script_keypad_handler_entry: void_mut_pointer  # CCScriptHandlerEntry
    script_accelerometer_handler_entry: void_mut_pointer  # CCScriptHandlerEntry

    touch_priority: int_t
    touch_mode: int_t  # enum
