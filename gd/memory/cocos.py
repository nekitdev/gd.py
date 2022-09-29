from gd.memory.base import Struct, struct
from gd.memory.data import Bool, Float, Int, MutArrayData, MutPointerData, StructData, UByte, UInt, Void


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
    array = MutPointerData(MutArrayData(MutPointerData(StructData(CCObject))))


@struct()
class CCArray(CCObject):
    data = MutPointerData(StructData(CCArrayStruct))


@struct(virtual=True)
class CCNode(CCObject):
    rotation_x = Float()
    rotation_y = Float()
    scale_x = Float()
    scale_y = Float()

    vertex_z = Float()

    position = StructData(CCPoint)

    skew_x = Float()
    skew_y = Float()

    anchor_in_points = StructData(CCPoint)
    anchor = StructData(CCPoint)

    content_size = StructData(CCSize)

    additional_transform = StructData(CCAffineTransform)
    transform = StructData(CCAffineTransform)
    inverse = StructData(CCAffineTransform)

    camera = MutPointerData(Void())  # CCCamera*

    grid = MutPointerData(Void())  # CCGridBase*

    z_order = Int()

    children = MutPointerData(StructData(CCArray))

    parent = MutPointerData(Void())  # CCNode*

    user_data = MutPointerData(Void())  # void
    user_object = MutPointerData(StructData(CCObject))

    shader_program = MutPointerData(Void())  # CCGLProgram*

    server_state = Int()  # enum

    order_of_arrival = UInt()

    scheduler = MutPointerData(Void())  # CCScheduler*

    action_manager = MutPointerData(Void())  # CCActionManager*

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

    component_container = MutPointerData(Void())  # CCComponentContainer*


@struct(virtual=True)
class CCNodeRGBA(CCNode):
    displayed_opacity = UByte()
    real_opacity = UByte()

    displayed_color = StructData(ColorRGB)
    real_color = StructData(ColorRGB)

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

    script_touch_handler_entry = MutPointerData(Void())  # CCTouchScriptHandlerEntry*
    script_keypad_handler_entry = MutPointerData(Void())  # CCScriptHandlerEntry*
    script_accelerometer_handler_entry = MutPointerData(Void())  # CCScriptHandlerEntry*

    touch_priority = Int()
    touch_mode = Int()  # enum
