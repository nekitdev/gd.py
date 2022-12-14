"""An example that shows fetching created level names.
Author: nekitdev
"""

import gd

LEVEL = "{index:<{align}} | {level.name}"

database = gd.api.save.load()  # load local database (save)

levels = database.created_levels  # get created levels

# align indexes using the largest index
align = len(str(len(levels)))

for index, level in enumerate(levels):  # for each level, print level ID and name, formatted
    # 0 | Level
    # 1 | Another Level
    print(LEVEL.format(index=index, align=align, level=level))
