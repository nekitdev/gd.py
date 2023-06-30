from typing import Any, List, Type, TypeVar

from attrs import define, field
from funcs.application import partial
from iters.iters import iter
from typing_aliases import StringDict, StringMapping
from typing_extensions import Literal, TypeGuard

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import (
    DEFAULT_AMOUNT,
    DEFAULT_COMPLETED,
    DEFAULT_DIAMONDS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_ID,
    DEFAULT_LOCATION,
    DEFAULT_MAGIC,
    DEFAULT_QUEST_ORDER,
    EMPTY,
)
from gd.enums import ByteOrder, InternalType, RewardItemType
from gd.string_utils import snake_to_camel

__all__ = ("Reward", "RewardItem", "Quest")

DEFAULT_COUNT = 0

ORDER_MASK = 0b00000011
ID_MASK = 0b00001100
COMPLETED_BIT = 0b10000000

ID_SHIFT = ORDER_MASK.bit_length()

INTERNAL_TYPE = "kCEK"

QUEST_ID = "1"
QUEST_AMOUNT = "2"
QUEST_TARGET_AMOUNT = "3"
QUEST_DIAMONDS = "4"
QUEST_COUNT = "5"
QUEST_COMPLETED = "6"
QUEST_NAME = "7"
QUEST_ORDER = "8"

Q = TypeVar("Q", bound="Quest")


@define()
class Quest(Binary):
    id: int = DEFAULT_ID
    amount: int = DEFAULT_AMOUNT
    target_amount: int = DEFAULT_AMOUNT
    diamonds: int = DEFAULT_DIAMONDS
    count: int = DEFAULT_COUNT
    completed: bool = DEFAULT_COMPLETED
    name: str = EMPTY
    quest_order: int = DEFAULT_QUEST_ORDER

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def from_binary(
        cls: Type[Q],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> Q:
        completed_bit = COMPLETED_BIT

        reader = Reader(binary, order)

        value = reader.read_u8()

        quest_order = value & ORDER_MASK

        id = (value & ID_MASK) >> ID_SHIFT

        completed = value & completed_bit == completed_bit

        amount = reader.read_u16()
        target_amount = reader.read_u16()

        diamonds = reader.read_u8()

        count = reader.read_u16()

        name_length = reader.read_u8()

        name = reader.read(name_length).decode(encoding, errors)

        return cls(
            quest_order=quest_order,
            id=id,
            amount=amount,
            target_amount=target_amount,
            diamonds=diamonds,
            count=count,
            completed=completed,
            name=name,
        )

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary, order)

        value = self.quest_order

        value |= self.id << ID_SHIFT

        if self.is_completed():
            value |= COMPLETED_BIT

        writer.write_u8(value)

        writer.write_u16(self.amount)
        writer.write_u16(self.target_amount)

        writer.write_u8(self.diamonds)

        writer.write_u16(self.count)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data))

        writer.write(data)

    @classmethod
    def from_robtop_data(cls: Type[Q], data: StringMapping[Any]) -> Q:  # type: ignore
        quest_order = data.get(QUEST_ORDER, DEFAULT_QUEST_ORDER)
        id = data.get(QUEST_ID, DEFAULT_ID)
        amount = data.get(QUEST_AMOUNT, DEFAULT_AMOUNT)
        target_amount = data.get(QUEST_TARGET_AMOUNT, DEFAULT_AMOUNT)
        diamonds = data.get(QUEST_DIAMONDS, DEFAULT_DIAMONDS)
        count = data.get(QUEST_COUNT, DEFAULT_COUNT)
        completed = data.get(QUEST_COMPLETED, DEFAULT_COMPLETED)
        name = data.get(QUEST_NAME, EMPTY)

        return cls(
            quest_order=quest_order,
            id=id,
            amount=amount,
            target_amount=target_amount,
            diamonds=diamonds,
            count=count,
            completed=completed,
            name=name,
        )

    def to_robtop_data(self) -> StringDict[Any]:
        data = {
            INTERNAL_TYPE: InternalType.QUEST.value,
            QUEST_ID: self.id,
            QUEST_AMOUNT: self.amount,
            QUEST_TARGET_AMOUNT: self.target_amount,
            QUEST_DIAMONDS: self.diamonds,
            QUEST_COUNT: self.count,
            QUEST_COMPLETED: self.is_completed(),
            QUEST_NAME: self.name,
            QUEST_ORDER: self.quest_order,
        }

        return data

    def is_completed(self) -> bool:
        return self.completed


REWARD_ITEM_TYPE = "1"
REWARD_CUSTOM_ID = "2"
REWARD_AMOUNT = "3"
REWARD_MAGIC = "4"

R = TypeVar("R", bound="Reward")


@define()
class Reward(Binary):
    item_type: RewardItemType = RewardItemType.DEFAULT
    custom_id: int = DEFAULT_ID
    amount: int = DEFAULT_AMOUNT
    magic: int = DEFAULT_MAGIC

    @classmethod
    def from_binary(
        cls: Type[R],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> R:
        reader = Reader(binary, order)

        item_type_value = reader.read_u8()

        item_type = RewardItemType(item_type_value)

        custom_id = reader.read_u16()

        amount = reader.read_u16()

        magic = reader.read_i32()

        return cls(item_type=item_type, custom_id=custom_id, amount=amount, magic=magic)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u8(self.item_type.value)

        writer.write_u16(self.custom_id)

        writer.write_u16(self.amount)

        writer.write_i32(self.magic)

    @classmethod
    def from_robtop_data(cls: Type[R], data: StringMapping[Any]) -> R:  # type: ignore
        item_type_option = data.get(REWARD_ITEM_TYPE)

        if item_type_option is None:
            item_type = RewardItemType.DEFAULT

        else:
            item_type = RewardItemType(item_type_option)

        custom_id = data.get(REWARD_CUSTOM_ID, DEFAULT_ID)
        amount = data.get(REWARD_AMOUNT, DEFAULT_AMOUNT)
        magic = data.get(REWARD_MAGIC, DEFAULT_MAGIC)

        return cls(item_type=item_type, custom_id=custom_id, amount=amount, magic=magic)

    def to_robtop_data(self) -> StringDict[Any]:
        item_type = self.item_type

        data = {
            INTERNAL_TYPE: InternalType.REWARD.value,
            REWARD_ITEM_TYPE: item_type.value,
            REWARD_CUSTOM_ID: self.custom_id,
            REWARD_AMOUNT: self.amount,
            REWARD_MAGIC: self.magic,
        }

        return data


IS_ARRAY = snake_to_camel("_is_arr")

KEY = "k_{}"
key = KEY.format


def is_true(item: Any) -> TypeGuard[Literal[True]]:
    return item is True


REWARD_ITEM_ID = "1"
REWARD_ITEM_LOCATION = "2"
REWARD_ITEM_REWARDS = "3"

RI = TypeVar("RI", bound="RewardItem")


@define()
class RewardItem(Binary):
    id: int = field(default=DEFAULT_ID)
    location: int = field(default=DEFAULT_LOCATION)
    rewards: List[Reward] = field(factory=list)

    @classmethod
    def from_binary(
        cls: Type[RI],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> RI:
        reader = Reader(binary, order)

        id = reader.read_u16()

        location = reader.read_u8()

        rewards_length = reader.read_u8()

        reward_from_binary = partial(Reward.from_binary, binary, order, version)

        rewards = iter.repeat_exactly_with(reward_from_binary, rewards_length).list()

        return cls(id=id, location=location, rewards=rewards)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        writer.write_u16(self.id)

        writer.write_u8(self.location)

        rewards = self.rewards

        writer.write_u8(len(rewards))

        for reward in rewards:
            reward.to_binary(binary, order, version)

    @classmethod
    def from_robtop_data(cls: Type[RI], data: StringMapping[Any]) -> RI:  # type: ignore
        id = data.get(REWARD_ITEM_ID, DEFAULT_ID)
        location = data.get(REWARD_ITEM_LOCATION, DEFAULT_LOCATION)

        rewards_data = data.get(REWARD_ITEM_REWARDS, {})

        rewards = (
            iter(rewards_data.values()).skip_while(is_true).map(Reward.from_robtop_data).list()
        )

        return cls(id=id, location=location, rewards=rewards)

    def to_robtop_data(self) -> StringDict[Any]:
        data: StringDict[Any] = {
            INTERNAL_TYPE: InternalType.REWARD_ITEM.value,
            REWARD_ITEM_ID: self.id,
            REWARD_ITEM_LOCATION: self.location,
        }

        rewards_data: StringDict[Any] = {IS_ARRAY: True}

        for index, reward in enumerate(self.rewards):
            rewards_data[key(index)] = reward.to_robtop_data()

        data[REWARD_ITEM_REWARDS] = rewards_data

        return data
