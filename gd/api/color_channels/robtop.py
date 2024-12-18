from gd.internals.robtop.core import concat_iterable_with, split_iterable_with

COLOR_CHANNEL_SEPARATOR = "_"

split_color_channel = split_iterable_with(COLOR_CHANNEL_SEPARATOR)
concat_color_channel = concat_iterable_with(COLOR_CHANNEL_SEPARATOR)

COLOR_CHANNELS_SEPARATOR = "|"

split_color_channels = split_iterable_with(COLOR_CHANNELS_SEPARATOR)
concat_color_channels = concat_iterable_with(COLOR_CHANNELS_SEPARATOR)
