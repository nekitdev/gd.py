import gd

database = gd.api.save.load()  # load local database (save)

levels = database.get_created_levels()  # get created levels

# align indexes using the largest one
index_align = len(str(len(levels)))
# align names using the longest one
name_align = max((len(level.name) for level in levels), default=0)

for index, level in enumerate(levels):  # for each level, print formatted line
    # 0 |      Something | ID: 13
    # 1 | Something Else | ID: 42
    print(f"{index:<{index_align}} | {level.name:>{name_align}} | ID: {level.id}")
