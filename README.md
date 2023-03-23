# UDM-REST API containers

The CA certificate can simply be downloaded from a UCS server:
```bash
curl "http://${LDAP_SERVER_IP}/ucs-root-ca.crt" -o "CAcert.pem"
```

Create your environment `.env.univention-directory-manager-rest` file
by running the script and pointing it to your UCS host:
```bash
./build-dot-env.py root@<YOUR_UCS_HOST>
```
This will fetch the necessary environment and UCR variables.

Now, build and run your container:
```bash
docker compose up --detach --remove-orphans --build
```

Point your browser to http://localhost:9979/udm/ and enjoy!


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
