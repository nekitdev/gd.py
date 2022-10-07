from gd.memory.arrays import DynamicFill, MutArrayData
from gd.memory.base import Struct, StructData, struct
from gd.memory.data import Bool, Float, Int, UByte, UInt
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
class CCRectangle(Struct):
    origin = Field(StructData(CCPoint))
    size = Field(StructData(CCSize))


@struct()
class CCColor3B(Struct):
    r = Field(UByte())
    g = Field(UByte())
    b = Field(UByte())


@struct()
class CCColor4B(Struct):
    r = Field(UByte())
    g = Field(UByte())
    b = Field(UByte())
    a = Field(UByte())


@struct()
class CCVertex3F(Struct):
    x = Field(Float())
    y = Field(Float())
    z = Field(Float())


@struct()
class CCTex2F(Struct):
    u = Field(Float())
    v = Field(Float())


@struct()
class CCV3F_C4B_T2F(Struct):
    vertex = Field(StructData(CCVertex3F))
    color = Field(StructData(CCColor4B))
    tex = Field(StructData(CCTex2F))


@struct()
class CCV3F_C4B_T2F_Quad(Struct):
    top_left = Field(StructData(CCV3F_C4B_T2F))
    bottom_left = Field(StructData(CCV3F_C4B_T2F))
    top_right = Field(StructData(CCV3F_C4B_T2F))
    bottom_right = Field(StructData(CCV3F_C4B_T2F))


@struct()
class CCBlendFunction(Struct):
    source = Field(UInt())
    destination = Field(UInt())


@struct()
class CCAffineTransform(Struct):
    a = Field(Float())
    b = Field(Float())
    c = Field(Float())
    d = Field(Float())
    translate_x = Field(Float())
    translate_y = Field(Float())


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
class CCRGBAProtocol(Struct):
    pass


@struct(virtual=True)
class CCBlendProtocol(Struct):
    pass


@struct(virtual=True)
class CCTextureProtocol(CCBlendProtocol):
    pass


@struct(virtual=True)
class CCNodeRGBA(CCRGBAProtocol, CCNode):
    displayed_opacity = Field(UByte())
    real_opacity = Field(UByte())

    displayed_color = Field(StructData(CCColor3B))
    real_color = Field(StructData(CCColor3B))

    cascade_color_enabled = Field(Bool())
    cascade_opacity_enabled = Field(Bool())


@struct(virtual=True)
class CCSpriteBatchNode(CCTextureProtocol, CCNode):
    texture_atlas = Field(MutPointerData(Void()))  # CCTextureAtlas*
    blend_function = Field(StructData(CCBlendFunction))

    descendants = Field(MutPointerData(StructData(CCArray)))

    manual_sort_children = Field(Bool())
    manual_sort_all_children_dirty = Field(Bool())


@struct(virtual=True)
class CCSprite(CCTextureProtocol, CCNodeRGBA):
    texture_atlas = Field(MutPointerData(Void()))  # CCTextureAtlas*
    atlas_index = Field(UInt())
    batch_node = Field(MutPointerData(StructData(CCSpriteBatchNode)))

    dirty = Field(Bool())
    recursive_dirty = Field(Bool())
    has_children = Field(Bool())
    should_be_hidden = Field(Bool())

    transform_to_batch_node = Field(StructData(CCAffineTransform))

    blend_function = Field(StructData(CCBlendFunction))

    texture = Field(MutPointerData(Void()))  # CCTexture2D*

    rectangle = Field(StructData(CCRectangle))

    rectangle_rotated = Field(Bool())

    offset_position = Field(StructData(CCPoint))
    unflipped_offset_position_from_center = Field(StructData(CCPoint))

    quad = Field(StructData(CCV3F_C4B_T2F_Quad))

    opacity_modify_rgb = Field(Bool())

    flip_x = Field(Bool())
    flip_y = Field(Bool())

    do_not_draw = Field(Bool())

    top_left_mod = Field(Float())
    top_right_mod = Field(Float())
    bottom_left_mod = Field(Float())
    bottom_right_mod = Field(Float())

    _pad_0 = Field(DynamicFill(16))

    unknown_bool = Field(Bool())
    unknown = Field(Int())


@struct(virtual=True)
class CCSpritePlus(CCSprite):
    followers = Field(MutPointerData(StructData(CCArray)))
    following = Field(MutPointerData(Void()))  # CCSpritePlus*

    has_followers = Field(Bool())
    scale_followers = Field(Bool())
    flip_followers = Field(Bool())


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


@struct()
class CCNodeContainer(CCNode):
    pass
