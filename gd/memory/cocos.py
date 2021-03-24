# type: ignore

from gd.memory.marker import (
    Struct, mut_array, mut_pointer, bool_t, ubyte_t, float_t, int_t, uint_t, this, void
)


class CCPoint(Struct):
    x: float_t
    y: float_t


class CCSize(Struct):
    width: float_t
    height: float_t


class CCRect(Struct):
    origin: CCPoint
    size: CCSize


class Matrix4(Struct):  # 4 x 4 matrix
    matrix: mut_array(float_t, 4 * 4)


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


class CCArrayStruct(Struct):
    length: uint_t
    capacity: uint_t
    # this is actually CCObject double pointer,
    # but since we do not have indexing or iterating pointers implemented,
    # we instead make it point to an array of pointers
    array: mut_pointer(mut_array(mut_pointer(CCObject)))


class CCArray(CCObject):
    data: mut_pointer(CCArrayStruct)


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

    camera: mut_pointer(void)  # CCCamera

    grid: mut_pointer(void)  # CCGridBase

    z_order: int_t

    children: mut_pointer(CCArray)

    parent: mut_pointer(this)

    user_data: mut_pointer(void)  # void
    user_object: mut_pointer(CCObject)

    shader_program: mut_pointer(void)  # CCGLProgram

    server_state: int_t  # enum

    order_of_arrival: uint_t

    scheduler: mut_pointer(void)  # CCScheduler

    action_manager: mut_pointer(void)  # CCActionManager

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

    component_container: mut_pointer(void)  # CCComponentContainer


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

    script_touch_handler_entry: mut_pointer(void)  # CCTouchScriptHandlerEntry
    script_keypad_handler_entry: mut_pointer(void)  # CCScriptHandlerEntry
    script_accelerometer_handler_entry: mut_pointer(void)  # CCScriptHandlerEntry

    touch_priority: int_t
    touch_mode: int_t  # enum
