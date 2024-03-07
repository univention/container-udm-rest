# UDM Rest API Python Client

This container contains the needed Python client libraries, so that it is easy
to run Python scripts against a given UDM Rest API endpoint.

There is also a `udm-cli` that can be used to interact directly with the udm client by running:


## python client example usage

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

## udm-cli example usage

```shell
docker run gitregistry.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/udm-cli help
```


### Working with `ucs` sources

Assuming that you have the repository `ucs` cloned as a sibling to this
repository, then you can mount the Python source code of the api client into
your container by adding the following content into your
`docker-compose.override.yaml`:

```yaml
  api-client:
    volumes:
      - "../ucs/management/univention-directory-manager-rest/src/univention/admin/rest:/usr/lib/python3/dist-packages/univention/admin/rest"
```

This allows you to easily debug the code if you suspect that there is an issue
in the Python client of the udm api.
