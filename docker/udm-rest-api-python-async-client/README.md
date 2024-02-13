# UDM REST API Python Client

This container contains the needed Python client libraries, so that it is easy
to run Python scripts against a given UDM REST API endpoint.


## Example usage

Start a `python3` interpreter:

```shell
docker compose run --rm -it api-client-async python3
```

Then import and use the api client:

```python
import asyncio
from univention.admin.rest.async_client import UDM
uri = 'http://localhost/univention/udm/'

async def main():
    async with UDM.http(uri, 'Administrator', 'univention') as udm:
        module = await udm.get('users/user')
        print(f'Found {module}')
        objs = module.search()
        async for obj in objs:
            if not obj:
                continue
            obj = await obj.open()
            print(f'Object {obj}')
            for group in obj.objects.groups:
                grp = await group.open()
                print(f'Group {grp}')

asyncio.run(main())
```


### Working with `ucs` sources

Assuming that you have the repository `ucs` cloned as a sibling to this
repository, then you can mount the Python source code of the api client into
your container by adding the following content into your
`docker-compose.override.yaml`:

```yaml
  api-client-async:
    volumes:
      - "../ucs/management/univention-directory-manager-rest/src/univention/admin/rest:/usr/lib/python3/dist-packages/univention/admin/rest"
```

This allows you to easily debug the code if you suspect that there is an issue
in the Python client of the UDM API.
