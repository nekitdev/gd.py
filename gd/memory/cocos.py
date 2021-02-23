# type: ignore

from gd.memory.marker import Struct, mut_array, mut_pointer, bool_t, float_t, int_t, uint_t, void


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
    array: mut_pointer(mut_array(CCObject))


class CCArray(CCObject):
    data: mut_pointer(CCArrayStruct)


class CCNode(CCObject):
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

    parent: mut_pointer(void)  # CCNode <- recursive reference!

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
