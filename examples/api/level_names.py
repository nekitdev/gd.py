import gd

database = gd.api.save.load()  # load local database (save)

levels = database.get_created_levels()  # get created levels

# align indexes using the largest one
align = len(str(len(levels)))

for index, level in enumerate(levels):  # for each level, print formatted line
    # 0 | Something
    # 1 | Something Else
    print(f"{index:<{align}} | {level.name}")
