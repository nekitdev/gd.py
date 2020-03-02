import os

import gd

name, password = (
    os.getenv('GDUSER'), os.getenv('GDPASSWORD')
)

client = gd.Client()

if name is not None and password is not None:
    client.run(client.login(name, password))
