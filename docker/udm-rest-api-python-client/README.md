# UDM Rest API Python Client

This container contains the needed Python client libraries, so that it is easy
to run Python scripts against a given UDM Rest API endpoint.


## Example usage

Start a `python3` interpreter:

```shell
docker compose run --rm -it api-client python3
```

Then import and use the api client:

```python
from univention.admin.rest.client import *

ldap_base = "dc=univention-organization,dc=intranet"
uri = 'http://udm-rest-api.default/udm/'
udm = UDM.http(uri, 'cn=admin', 'your-password')

container = udm.get("container/cn")
x = container.get("cn=test," + ldap_base)
```
