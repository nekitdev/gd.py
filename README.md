# gd.py
gd.py Is A Geometry Dash API Wrapper For Python.
# AuthClient Example:
```python
import gd #importing gd module
client = gd.client() #library is based on gd.client() 
auth_client = client.login(user='User', password='password') #tries to log in with given 'user' and 'pass'
#returns 'gd.AuthClient()' on success
print(auth_client.name, auth_client.password) #prints 'User', 'password' (if succeeded and 'gd.AuthClient()' was returned)
```

