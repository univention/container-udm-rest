# UDM-REST API containers

The CA certificate can simply be downloaded from a UCS server:
```bash
mkdir -p /etc/univention/ssl/ucsCA/
curl "http://${LDAP_SERVER_IP}/ucs-root-ca.crt" -o "CAcert.pem"
echo "CA_CERT_FILE=CAcert.pem" >> .env.univention-directory-manager-rest
```

LDAP Credentials/Settings can be obtained from the UCS Primary via:
```bash
eval "$(univention-config-registry shell)"
echo "LDAP_URI=ldap://${ldap_master}:${ldap_master_port}" >> .env.univention-directory-manager-rest
echo "LDAP_BASE=${ldap_base}" >> .env.univention-directory-manager-rest
echo "LDAP_MACHINE_PASSWORD=$(cat /etc/machine.secret)" >> .env.univention-directory-manager-rest
echo "LDAP_ADMIN_PASSWORD=$(cat /etc/ldap.secret)" >> .env.univention-directory-manager-rest
```

Environment variables can simply be obtained from the DC Primary via:

```bash
univention-config-registry dump >> .env.univention-directory-manager-rest
```
