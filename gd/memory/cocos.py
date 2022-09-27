from gd.memory.base import Struct, struct
from gd.memory.fields import Bool, Float, Int, MutArrayField, MutPointerField, StructField, UByte, UInt, Void


@struct()
class CCPoint(Struct):
    x = Float()
    y = Float()


@struct()
class CCSize(Struct):
    width = Float()
    height = Float()


@struct()
class CCAffineTransform(Struct):
    a = Float()
    b = Float()
    c = Float()
    d = Float()
    translate_x = Float()
    translate_y = Float()


@struct()
class ColorRGB(Struct):
    r = UByte()
    g = UByte()
    b = UByte()


@struct(virtual=True)
class CCCopying(Struct):
    pass


@struct()
class CCObject(CCCopying):
    id = UInt()
    ref_id = Int()

    tag = UInt()  # modified

    ref_count = UInt()
    auto_release_count = UInt()

    object_type = Int()  # enum  # modified
    index_in_array = UInt()


@struct()
class CCArrayStruct(Struct):
    length = UInt()
    capacity = UInt()
    # this is actually CCObject double pointer,
    # but since we do not have indexing or iterating pointers implemented,
    # we instead make it point to an array of pointers
    array = MutPointerField(MutArrayField(MutPointerField(StructField(CCObject))))


@struct()
class CCArray(CCObject):
    data = MutPointerField(StructField(CCArrayStruct))


@struct(virtual=True)
class CCNode(CCObject):
    rotation_x = Float()
    rotation_y = Float()
    scale_x = Float()
    scale_y = Float()

    vertex_z = Float()

    position = StructField(CCPoint)

    skew_x = Float()
    skew_y = Float()

    anchor_in_points = StructField(CCPoint)
    anchor = StructField(CCPoint)

    content_size = StructField(CCSize)

    additional_transform = StructField(CCAffineTransform)
    transform = StructField(CCAffineTransform)
    inverse = StructField(CCAffineTransform)

    camera = MutPointerField(Void())  # CCCamera*

    grid = MutPointerField(Void())  # CCGridBase*

    z_order = Int()

    children = MutPointerField(StructField(CCArray))

    parent = MutPointerField(Void())  # CCNode*

    user_data = MutPointerField(Void())  # void
    user_object = MutPointerField(StructField(CCObject))

    shader_program = MutPointerField(Void())  # CCGLProgram*

    server_state = Int()  # enum

    order_of_arrival = UInt()

    scheduler = MutPointerField(Void())  # CCScheduler*

    action_manager = MutPointerField(Void())  # CCActionManager*

    running = Bool()

    transform_dirty = Bool()
    inverse_dirty = Bool()
    additional_transform_dirty = Bool()
    visible = Bool()

    ignore_anchor_point_for_position = Bool()

    reorder_child_dirty = Bool()

    script_handler = Int()
    update_script_handler = Int()
    script_type = Int()  # enum

    component_container = MutPointerField(Void())  # CCComponentContainer*


@struct(virtual=True)
class CCNodeRGBA(CCNode):
    displayed_opacity = UByte()
    real_opacity = UByte()

    displayed_color = StructField(ColorRGB)
    real_color = StructField(ColorRGB)

    cascade_color_enabled = Bool()
    cascade_opacity_enabled = Bool()


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
    touch_enabled = Bool()
    accelerometer_enabled = Bool()
    keypad_enabled = Bool()
    keyboard_enabled = Bool()
    mouse_enabled = Bool()

    script_touch_handler_entry = MutPointerField(Void())  # CCTouchScriptHandlerEntry*
    script_keypad_handler_entry = MutPointerField(Void())  # CCScriptHandlerEntry*
    script_accelerometer_handler_entry = MutPointerField(Void())  # CCScriptHandlerEntry*

    touch_priority = Int()
    touch_mode = Int()  # enum
