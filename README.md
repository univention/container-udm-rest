# UDM-REST API containers

The CA certificate can simply be downloaded from a UCS server:
```bash
curl "http://${LDAP_SERVER_IP}/ucs-root-ca.crt" -o "CAcert.pem"
```

Create your environment `.env.univention-directory-manager-rest` file
by running the script and pointing it to your UCS host:
```bash
./build_dot_env.py root@<YOUR_UCS_HOST>
```
This will fetch the necessary environment and UCR variables.

Now, build and run your container:
```bash
docker compose up --detach --remove-orphans --build
```

Point your browser to http://localhost:9979/udm/ and enjoy!


## Linting

You can run the pre-commit checker as follows:
```bash
docker compose run --rm pre-commit
```


## Environment Variables

- `CA_CERT_FILE=/run/secrets/ca_cert`

   Path the the .pem file containing the server's certificate

- `TLS_REQCERT=demand`

   ???

- `LDAP_URI`

   URL of the LDAP server (e.g. `ldap://host:port`)

- `LDAP_BASE`

   Base DN (e.g. `dc=univention,dc=intranet`)

- `LDAP_MACHINE_PASSWORD`

  From `/etc/machine.secret`

- `LDAP_ADMIN_PASSWORD`

  From `/etc/ldap.secret`

- `domainname`

  External domain name of the container.

  Used for assembling the FQDN in OpenAPI.

- `hostname`

  External host name of the container.

  Used for assembling the FQDN in OpenAPI.

- `directory/manager/rest/debug/level`

  Log level of the REST API server (default: `4` for info level).

  Larger values are more verbose.


## Implementation Status

### UDM Modules

The list of modules on the front page is generated [here](https://git.knut.univention.de/univention/ucs/-/blob/5.0-3/management/univention-directory-manager-rest/src/univention/admin/rest/module.py#L2116).
A scan of the modules present in the filesystem happens [here](https://git.knut.univention.de/univention/ucs/-/blob/5.0-3/management/univention-directory-manager-modules/modules/univention/admin/modules.py#L121).

Currently supported are the default Univention UDM modules
which are installed in `/usr/lib/python3/dist-packages/univention/admin/handlers/`,
with these exceptions:
  - *AppCenter:* \
    The handler is part of the package `univention-management-console-module-appcenter`,
    but it is unclear whether installing it makes sense in the containerized context.
  - *Portal:* \
    To be clarified. I do not know how the handler is installed in UCS... ¯\\_(ツ)_/¯

### Listener Mechanism

It is to be clarified,
if/how the listener mechanism can be supported,
or whether the provisioning architecture will take its place.
