# udm-rest-api

A Helm chart for the UDM REST API

- **Version**: 0.1.0
- **Type**: application
- **AppVersion**: 10.0.6-1
- **Homepage:** <https://www.univention.de/>

## TL;DR

```console
helm upgrade --install udm-rest-api oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/helm/udm-rest-api
```

## Introduction

This chart does install the REST API for the Univention Directory Manager.

The server provides an abstraction layer for interacting with the LDAP.

## Installing

To install the chart with the release name `udm-rest-api`:

```console
helm upgrade --install udm-rest-api oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/helm/udm-rest-api
```

## Uninstalling

To uninstall the chart with the release name `udm-rest-api`:

```console
helm uninstall udm-rest-api
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/common-helm/helm | common | ^0.2.0 |

## Values

<table>
	<thead>
		<th>Key</th>
		<th>Type</th>
		<th>Default</th>
		<th>Description</th>
	</thead>
	<tbody>
		<tr>
			<td>affinity</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>environment</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>fullnameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.loadJoinData</td>
			<td>object</td>
			<td><pre lang="json">
{
  "imagePullPolicy": "Always",
  "registry": "registry.souvap-univention.de",
  "repository": "souvap/tooling/images/udm-rest-api/udm-rest-api-load-join-data",
  "tag": "0.1.0"
}
</pre>
</td>
			<td>Image used to load the join data</td>
		</tr>
		<tr>
			<td>image.registry</td>
			<td>string</td>
			<td><pre lang="json">
"registry.souvap-univention.de"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"souvap/tooling/images/udm-rest-api/udm-rest-api"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"0.1.0"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>ingress</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {
    "nginx.ingress.kubernetes.io/rewrite-target": "/$1",
    "nginx.ingress.kubernetes.io/use-regex": "true"
  },
  "enabled": false,
  "ingressClassName": "nginx",
  "paths": [
    {
      "path": "/univention/(udm/.*)",
      "pathType": "Prefix"
    }
  ],
  "tls": {
    "enabled": true,
    "secretName": ""
  }
}
</pre>
</td>
			<td>Kubernetes ingress</td>
		</tr>
		<tr>
			<td>ingress.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Set this to `true` in order to enable the installation of Ingress related objects.</td>
		</tr>
		<tr>
			<td>ingress.paths</td>
			<td>list</td>
			<td><pre lang="json">
[
  {
    "path": "/univention/(udm/.*)",
    "pathType": "Prefix"
  }
]
</pre>
</td>
			<td>The hostname. This parameter has to be supplied. Example `udm.example.com`. host: "sso.example.com"</td>
		</tr>
		<tr>
			<td>istio.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Set this to `true` in order to enable the installation of Istio related objects.</td>
		</tr>
		<tr>
			<td>istio.gateway.annotations</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.externalGatewayName</td>
			<td>string</td>
			<td><pre lang="json">
"swp-istio-gateway"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.selectorIstio</td>
			<td>string</td>
			<td><pre lang="json">
"ingressgateway"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.tls.httpsRedirect</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.gateway.tls.secretName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>istio.virtualService</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {},
  "enabled": true,
  "pathOverrides": [],
  "paths": [
    {
      "match": "prefix",
      "path": "/univention/udm/",
      "rewrite": "/udm/"
    }
  ]
}
</pre>
</td>
			<td>The hostname. This parameter has to be supplied. Example `udm.example`. host: "sso.example.com"</td>
		</tr>
		<tr>
			<td>mountSecrets</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nodeSelector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
120
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.liveness.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>probes.readiness.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>replicaCount</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.limits.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"4"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.limits.memory</td>
			<td>string</td>
			<td><pre lang="json">
"4Gi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.requests.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"250m"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.requests.memory</td>
			<td>string</td>
			<td><pre lang="json">
"512Mi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>securityContext</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.http.containerPort</td>
			<td>int</td>
			<td><pre lang="json">
9979
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.http.port</td>
			<td>int</td>
			<td><pre lang="json">
80
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.http.protocol</td>
			<td>string</td>
			<td><pre lang="json">
"TCP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.sessionAffinity.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.sessionAffinity.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
10800
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.type</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>udmRestApi</td>
			<td>object</td>
			<td><pre lang="json">
{
  "authGroups": {
    "dcBackup": null,
    "dcSlaves": null,
    "domainAdmins": null
  },
  "caCertFile": "/var/secrets/ca_cert",
  "debugLevel": "5",
  "domainname": null,
  "hostname": null,
  "ldapBaseDn": null,
  "ldapHost": null,
  "ldapHostDn": null,
  "ldapHostIp": null,
  "ldapPort": "389",
  "ldapSecretFile": "/var/secrets/ldap_secret",
  "loadJoinData": {
    "enabled": true
  },
  "machineSecretFile": "/var/secrets/machine_secret",
  "tlsMode": "secure"
}
</pre>
</td>
			<td>Application configuration of the UDM REST API</td>
		</tr>
		<tr>
			<td>udmRestApi.authGroups</td>
			<td>object</td>
			<td><pre lang="json">
{
  "dcBackup": null,
  "dcSlaves": null,
  "domainAdmins": null
}
</pre>
</td>
			<td>Authorized groups with special rights.</td>
		</tr>
		<tr>
			<td>udmRestApi.authGroups.dcBackup</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Set directory.manager.rest.authorized-groups.dc-backup Example: `"cn=DC Backup Hosts,cn=groups,dc=example,dc=com"`</td>
		</tr>
		<tr>
			<td>udmRestApi.authGroups.dcSlaves</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Set directory.manager.rest.authorized-groups.dc-slaves Example: `"cn=DC Slave Hosts,cn=groups,dc=example,dc=com"`</td>
		</tr>
		<tr>
			<td>udmRestApi.authGroups.domainAdmins</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Set directory.manager.rest.authorized-groups.domain-admins Example: `"cn=Domain Admins,cn=groups,dc=example,dc=com"`</td>
		</tr>
		<tr>
			<td>udmRestApi.caCertFile</td>
			<td>string</td>
			<td><pre lang="json">
"/var/secrets/ca_cert"
</pre>
</td>
			<td>Path to file with the CA certificate. (Not needed when `tlsReqCert` set to `"never"`.)</td>
		</tr>
		<tr>
			<td>udmRestApi.debugLevel</td>
			<td>string</td>
			<td><pre lang="json">
"5"
</pre>
</td>
			<td>Debug level of the UDM REST API server. (1 = errors only, 99 = most verbose)</td>
		</tr>
		<tr>
			<td>udmRestApi.domainname</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Domain name of the instance. Example: `example.org`</td>
		</tr>
		<tr>
			<td>udmRestApi.hostname</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Host name of the instance. Example: `souvap`</td>
		</tr>
		<tr>
			<td>udmRestApi.ldapBaseDn</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Base DN of the LDAP directory. Example: `"dc=example,dc=org"`</td>
		</tr>
		<tr>
			<td>udmRestApi.ldapHost</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Hostname of the LDAP server. Example: `"ucs-1234.univention.intranet"`</td>
		</tr>
		<tr>
			<td>udmRestApi.ldapHostDn</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>DN of the UMC instance. Example: `"cn=ucs-1234,cn=dc,cn=computers,dc=example,dc=org"`</td>
		</tr>
		<tr>
			<td>udmRestApi.ldapHostIp</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>IP address of the LDAP server. (This resolved the `ldapHost` in order to facilitate TLS certificate checks.) Example: `"10.200.0.1"`</td>
		</tr>
		<tr>
			<td>udmRestApi.ldapPort</td>
			<td>string</td>
			<td><pre lang="json">
"389"
</pre>
</td>
			<td>Port to connect to the LDAP server.</td>
		</tr>
		<tr>
			<td>udmRestApi.ldapSecretFile</td>
			<td>string</td>
			<td><pre lang="json">
"/var/secrets/ldap_secret"
</pre>
</td>
			<td>Path to file with the LDAP secret. (TODO: This may be unnecessary here.)</td>
		</tr>
		<tr>
			<td>udmRestApi.loadJoinData.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable loading of initial join data during installation and upgrade. This is usually required because it does roll out the initial structure of the LDAP directory.</td>
		</tr>
		<tr>
			<td>udmRestApi.machineSecretFile</td>
			<td>string</td>
			<td><pre lang="json">
"/var/secrets/machine_secret"
</pre>
</td>
			<td>Path to file with the LDAP machine secret.</td>
		</tr>
		<tr>
			<td>udmRestApi.tlsMode</td>
			<td>string</td>
			<td><pre lang="json">
"secure"
</pre>
</td>
			<td>Set desired TLS mode. Options: `"secure"`, `"unvalidated"`, `"off"`.</td>
		</tr>
	</tbody>
</table>

