# udm-rest-api

A Helm chart for the UDM REST API

- **Version**: 0.1.0
- **Type**: application
- **AppVersion**: 12.0.7
- **Homepage:** <https://www.univention.de/>

## TL;DR

```console
helm upgrade --install udm-rest-api oci://gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/helm/udm-rest-api
```

## Introduction

This chart does install the REST API for the Univention Directory Manager.

The server provides an abstraction layer for interacting with the LDAP.

## Installing

To install the chart with the release name `udm-rest-api`:

```console
helm upgrade --install udm-rest-api oci://gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/udm-rest-api/helm/udm-rest-api
```

## Uninstalling

To uninstall the chart with the release name `udm-rest-api`:

```console
helm uninstall udm-rest-api
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus/charts | nubus-common | 0.28.0 |

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
			<td>additionalAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>additionalLabels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>affinity</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Affinity for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity Note: podAffinityPreset, podAntiAffinityPreset, and nodeAffinityPreset will be ignored when it's set.</td>
		</tr>
		<tr>
			<td>blocklistCleanup</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "image": {
    "pullPolicy": null,
    "registry": null,
    "repository": "nubus-dev/images/blocklist-cleanup",
    "tag": "latest"
  },
  "schedule": "0 8 * * *"
}
</pre>
</td>
			<td>Settings to configure the UDM blocklist cleanup job</td>
		</tr>
		<tr>
			<td>blocklistCleanup.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable the blocklist cleanup cronjob.</td>
		</tr>
		<tr>
			<td>blocklistCleanup.image</td>
			<td>object</td>
			<td><pre lang="json">
{
  "pullPolicy": null,
  "registry": null,
  "repository": "nubus-dev/images/blocklist-cleanup",
  "tag": "latest"
}
</pre>
</td>
			<td>Container image configuration.</td>
		</tr>
		<tr>
			<td>blocklistCleanup.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>blocklistCleanup.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>blocklistCleanup.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus-dev/images/blocklist-cleanup"
</pre>
</td>
			<td>Container image repository.</td>
		</tr>
		<tr>
			<td>blocklistCleanup.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"latest"
</pre>
</td>
			<td>Container image tag.</td>
		</tr>
		<tr>
			<td>blocklistCleanup.schedule</td>
			<td>string</td>
			<td><pre lang="json">
"0 8 * * *"
</pre>
</td>
			<td>Cron schedule for the blocklist cleanup job.</td>
		</tr>
		<tr>
			<td>containerSecurityContext</td>
			<td>object</td>
			<td><pre lang="json">
{
  "allowPrivilegeEscalation": false,
  "capabilities": {
    "drop": [
      "ALL"
    ]
  },
  "enabled": true,
  "privileged": false,
  "readOnlyRootFilesystem": true,
  "runAsGroup": 1000,
  "runAsNonRoot": true,
  "runAsUser": 1000,
  "seccompProfile": {
    "type": "RuntimeDefault"
  }
}
</pre>
</td>
			<td>Security Context. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/</td>
		</tr>
		<tr>
			<td>containerSecurityContext.allowPrivilegeEscalation</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Enable container privileged escalation.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities</td>
			<td>object</td>
			<td><pre lang="json">
{
  "drop": [
    "ALL"
  ]
}
</pre>
</td>
			<td>Security capabilities for container.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities.drop</td>
			<td>list</td>
			<td><pre lang="json">
[
  "ALL"
]
</pre>
</td>
			<td>Linux capabilities to drop from the container.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.privileged</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Run container in privileged mode.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.readOnlyRootFilesystem</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Mounts the container's root filesystem as read-only.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>Process group id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsNonRoot</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Run container as a user.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsUser</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>Process user id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile</td>
			<td>object</td>
			<td><pre lang="json">
{
  "type": "RuntimeDefault"
}
</pre>
</td>
			<td>Set Seccomp profile.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile.type</td>
			<td>string</td>
			<td><pre lang="json">
"RuntimeDefault"
</pre>
</td>
			<td>Disallow custom Seccomp profile by setting it to RuntimeDefault.</td>
		</tr>
		<tr>
			<td>extensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Extensions to load. This will override the configuration in `global.extensions`.</td>
		</tr>
		<tr>
			<td>extraEnvVars</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar"</td>
		</tr>
		<tr>
			<td>extraSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify a secret to create (primarily intended to be used in development environments to provide custom certificates)</td>
		</tr>
		<tr>
			<td>extraVolumeMounts</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumeMounts.</td>
		</tr>
		<tr>
			<td>extraVolumes</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumes.</td>
		</tr>
		<tr>
			<td>fullnameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Provide a name to substitute for the full names of resources.</td>
		</tr>
		<tr>
			<td>global</td>
			<td>object</td>
			<td><pre lang="json">
{
  "configMapUcr": null,
  "extensions": [],
  "imagePullPolicy": null,
  "imagePullSecrets": [],
  "imageRegistry": "artifacts.software-univention.de",
  "ldap": {
    "baseDn": null,
    "connection": {
      "uri": null
    }
  },
  "nubusDeployment": false,
  "systemExtensions": []
}
</pre>
</td>
			<td>Global configuration options</td>
		</tr>
		<tr>
			<td>global.configMapUcr</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>ConfigMap name to read UCR values from.</td>
		</tr>
		<tr>
			<td>global.extensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Allows to configure extensions globally.</td>
		</tr>
		<tr>
			<td>global.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally.udm-rest-api.secretRef "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails.</td>
		</tr>
		<tr>
			<td>global.imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>global.imageRegistry</td>
			<td>string</td>
			<td><pre lang="json">
"artifacts.software-univention.de"
</pre>
</td>
			<td>Container registry address.</td>
		</tr>
		<tr>
			<td>global.ldap</td>
			<td>object</td>
			<td><pre lang="json">
{
  "baseDn": null,
  "connection": {
    "uri": null
  }
}
</pre>
</td>
			<td>Global ldap configuration</td>
		</tr>
		<tr>
			<td>global.ldap.baseDn</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The LDAP base DN to use when connecting. Example: "dc=univention-organization,dc=intranet"</td>
		</tr>
		<tr>
			<td>global.ldap.connection</td>
			<td>object</td>
			<td><pre lang="json">
{
  "uri": null
}
</pre>
</td>
			<td>LDAP connection configuration</td>
		</tr>
		<tr>
			<td>global.ldap.connection.uri</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The LDAP URI to connect to. Example: "ldap://example-ldap-server:389"</td>
		</tr>
		<tr>
			<td>global.nubusDeployment</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Indicates wether this chart is part of a Nubus deployment.</td>
		</tr>
		<tr>
			<td>global.systemExtensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Allows to configure system extensions globally.</td>
		</tr>
		<tr>
			<td>imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>ingress</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {
    "nginx.ingress.kubernetes.io/affinity": "none",
    "nginx.ingress.kubernetes.io/configuration-snippet-disabled": "rewrite ^/univention(/udm/.*)$ $1 break;\n",
    "nginx.ingress.kubernetes.io/proxy-buffer-size": "64k",
    "nginx.ingress.kubernetes.io/rewrite-target": "/$2$3",
    "nginx.ingress.kubernetes.io/use-regex": "true"
  },
  "certManager": {
    "enabled": true,
    "issuerRef": {
      "kind": "ClusterIssuer",
      "name": ""
    }
  },
  "enabled": true,
  "host": "",
  "ingressClassName": "",
  "paths": [
    {
      "path": "/(univention/)(udm/.*)$",
      "pathType": "ImplementationSpecific"
    }
  ],
  "tls": {
    "enabled": true,
    "secretName": ""
  }
}
</pre>
</td>
			<td>Define and create Kubernetes Ingress.  Ref.: https://kubernetes.io/docs/concepts/services-networking/ingress/</td>
		</tr>
		<tr>
			<td>ingress.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{
  "nginx.ingress.kubernetes.io/affinity": "none",
  "nginx.ingress.kubernetes.io/configuration-snippet-disabled": "rewrite ^/univention(/udm/.*)$ $1 break;\n",
  "nginx.ingress.kubernetes.io/proxy-buffer-size": "64k",
  "nginx.ingress.kubernetes.io/rewrite-target": "/$2$3",
  "nginx.ingress.kubernetes.io/use-regex": "true"
}
</pre>
</td>
			<td>Define custom ingress annotations. annotations:   nginx.ingress.kubernetes.io/rewrite-target: /</td>
		</tr>
		<tr>
			<td>ingress.annotations."nginx.ingress.kubernetes.io/affinity"</td>
			<td>string</td>
			<td><pre lang="json">
"none"
</pre>
</td>
			<td>Session affinity configuration.</td>
		</tr>
		<tr>
			<td>ingress.annotations."nginx.ingress.kubernetes.io/configuration-snippet-disabled"</td>
			<td>string</td>
			<td><pre lang="json">
"rewrite ^/univention(/udm/.*)$ $1 break;\n"
</pre>
</td>
			<td>NGINX configuration snippet (disabled).</td>
		</tr>
		<tr>
			<td>ingress.annotations."nginx.ingress.kubernetes.io/proxy-buffer-size"</td>
			<td>string</td>
			<td><pre lang="json">
"64k"
</pre>
</td>
			<td>Some responses of the UDM Rest API contain very large response headers</td>
		</tr>
		<tr>
			<td>ingress.annotations."nginx.ingress.kubernetes.io/rewrite-target"</td>
			<td>string</td>
			<td><pre lang="json">
"/$2$3"
</pre>
</td>
			<td>Rewrite target for URL path rewriting.</td>
		</tr>
		<tr>
			<td>ingress.annotations."nginx.ingress.kubernetes.io/use-regex"</td>
			<td>string</td>
			<td><pre lang="json">
"true"
</pre>
</td>
			<td>Enable regex matching for paths.</td>
		</tr>
		<tr>
			<td>ingress.certManager</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "issuerRef": {
    "kind": "ClusterIssuer",
    "name": ""
  }
}
</pre>
</td>
			<td>Request certificates via cert-manager.io annotation</td>
		</tr>
		<tr>
			<td>ingress.certManager.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable cert-manager.io annotaion.</td>
		</tr>
		<tr>
			<td>ingress.certManager.issuerRef</td>
			<td>object</td>
			<td><pre lang="json">
{
  "kind": "ClusterIssuer",
  "name": ""
}
</pre>
</td>
			<td>Issuer reference.</td>
		</tr>
		<tr>
			<td>ingress.certManager.issuerRef.kind</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIssuer"
</pre>
</td>
			<td>Type of Issuer, f.e. "Issuer" or "ClusterIssuer".</td>
		</tr>
		<tr>
			<td>ingress.certManager.issuerRef.name</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Name of cert-manager.io Issuer resource.</td>
		</tr>
		<tr>
			<td>ingress.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable creation of Ingress.</td>
		</tr>
		<tr>
			<td>ingress.host</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Define the Fully Qualified Domain Name (FQDN) where application should be reachable.</td>
		</tr>
		<tr>
			<td>ingress.ingressClassName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The Ingress controller class name.</td>
		</tr>
		<tr>
			<td>ingress.paths</td>
			<td>list</td>
			<td><pre lang="json">
[
  {
    "path": "/(univention/)(udm/.*)$",
    "pathType": "ImplementationSpecific"
  }
]
</pre>
</td>
			<td>Define the Ingress paths.</td>
		</tr>
		<tr>
			<td>ingress.paths[0]</td>
			<td>object</td>
			<td><pre lang="json">
{
  "path": "/(univention/)(udm/.*)$",
  "pathType": "ImplementationSpecific"
}
</pre>
</td>
			<td>Path pattern for the Ingress rule.</td>
		</tr>
		<tr>
			<td>ingress.paths[0].pathType</td>
			<td>string</td>
			<td><pre lang="json">
"ImplementationSpecific"
</pre>
</td>
			<td>Path type for the Ingress rule.</td>
		</tr>
		<tr>
			<td>ingress.tls</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "secretName": ""
}
</pre>
</td>
			<td>Secure an Ingress by specifying a Secret that contains a TLS private key and certificate.  Ref.: https://kubernetes.io/docs/concepts/services-networking/ingress/#tls</td>
		</tr>
		<tr>
			<td>ingress.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable TLS/SSL/HTTPS for Ingress.</td>
		</tr>
		<tr>
			<td>ingress.tls.secretName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The name of the kubernetes secret which contains a TLS private key and certificate. Hint: This secret is not created by this chart and must be provided.</td>
		</tr>
		<tr>
			<td>initResources</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Configure resource requests and limits for initContainers.</td>
		</tr>
		<tr>
			<td>ldap</td>
			<td>object</td>
			<td><pre lang="json">
{
  "auth": {
    "bindDn": "cn=admin,{{ default \"dc=univention-organization,dc=intranet\" .Values.global.ldap.baseDn }}",
    "existingSecret": {
      "keyMapping": {
        "password": null
      },
      "name": null
    },
    "password": null
  },
  "baseDn": "",
  "connection": {
    "uri": ""
  }
}
</pre>
</td>
			<td>LDAP Client configuration</td>
		</tr>
		<tr>
			<td>ldap.auth</td>
			<td>object</td>
			<td><pre lang="json">
{
  "bindDn": "cn=admin,{{ default \"dc=univention-organization,dc=intranet\" .Values.global.ldap.baseDn }}",
  "existingSecret": {
    "keyMapping": {
      "password": null
    },
    "name": null
  },
  "password": null
}
</pre>
</td>
			<td>LDAP authentication configuration.</td>
		</tr>
		<tr>
			<td>ldap.auth.bindDn</td>
			<td>string</td>
			<td><pre lang="json">
"cn=admin,{{ default \"dc=univention-organization,dc=intranet\" .Values.global.ldap.baseDn }}"
</pre>
</td>
			<td>Bind DN for LDAP authentication.</td>
		</tr>
		<tr>
			<td>ldap.auth.existingSecret</td>
			<td>object</td>
			<td><pre lang="json">
{
  "keyMapping": {
    "password": null
  },
  "name": null
}
</pre>
</td>
			<td>Configuration for using an existing secret for LDAP credentials.</td>
		</tr>
		<tr>
			<td>ldap.auth.existingSecret.keyMapping</td>
			<td>object</td>
			<td><pre lang="json">
{
  "password": null
}
</pre>
</td>
			<td>Key mapping for the existing secret.</td>
		</tr>
		<tr>
			<td>ldap.auth.existingSecret.keyMapping.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Key in the secret for the password.</td>
		</tr>
		<tr>
			<td>ldap.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Name of the existing secret.</td>
		</tr>
		<tr>
			<td>ldap.auth.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Password for LDAP authentication.</td>
		</tr>
		<tr>
			<td>ldap.baseDn</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The LDAP base DN to use when connecting. baseDn: "dc=univention-organization,dc=intranet"</td>
		</tr>
		<tr>
			<td>ldap.connection</td>
			<td>object</td>
			<td><pre lang="json">
{
  "uri": ""
}
</pre>
</td>
			<td>LDAP connection configuration.</td>
		</tr>
		<tr>
			<td>ldap.connection.uri</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The LDAP URI to connect to. uri: "ldap://my-ldap-server:389"</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "image": {
    "pullPolicy": null,
    "registry": null,
    "repository": "nubus-dev/images/ldap-update-univention-object-identifier",
    "tag": "latest"
  },
  "pythonLogLevel": "INFO",
  "suspend": true
}
</pre>
</td>
			<td>Job configuration for updating the univentionObjectIdentifier</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enables the job creation</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.image</td>
			<td>object</td>
			<td><pre lang="json">
{
  "pullPolicy": null,
  "registry": null,
  "repository": "nubus-dev/images/ldap-update-univention-object-identifier",
  "tag": "latest"
}
</pre>
</td>
			<td>Container image configuration.</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus-dev/images/ldap-update-univention-object-identifier"
</pre>
</td>
			<td>Container image repository.</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"latest"
</pre>
</td>
			<td>Container image tag.</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.pythonLogLevel</td>
			<td>string</td>
			<td><pre lang="json">
"INFO"
</pre>
</td>
			<td>Log Level for the Python script</td>
		</tr>
		<tr>
			<td>ldapUpdateUniventionObjectIdentifier.suspend</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Switch to suspend the job</td>
		</tr>
		<tr>
			<td>lifecycleHooks</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Lifecycle to automate configuration before or after startup.</td>
		</tr>
		<tr>
			<td>livenessProbe</td>
			<td>object</td>
			<td><pre lang="json">
{
  "failureThreshold": 10,
  "initialDelaySeconds": 15,
  "periodSeconds": 20,
  "successThreshold": 1,
  "tcpSocket": {
    "port": 9979
  },
  "timeoutSeconds": 5
}
</pre>
</td>
			<td>Configure extra options for containers probes.</td>
		</tr>
		<tr>
			<td>livenessProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>livenessProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td>Delay after container start until LivenessProbe is executed.</td>
		</tr>
		<tr>
			<td>livenessProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>livenessProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>livenessProbe.tcpSocket</td>
			<td>object</td>
			<td><pre lang="json">
{
  "port": 9979
}
</pre>
</td>
			<td>TCP socket configuration for the liveness probe.</td>
		</tr>
		<tr>
			<td>livenessProbe.tcpSocket.port</td>
			<td>int</td>
			<td><pre lang="json">
9979
</pre>
</td>
			<td>Port to check for liveness.</td>
		</tr>
		<tr>
			<td>livenessProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>nameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>String to partially override release name.</td>
		</tr>
		<tr>
			<td>nodeSelector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Node labels for pod assignment. Ref: https://kubernetes.io/docs/user-guide/node-selection/</td>
		</tr>
		<tr>
			<td>persistence</td>
			<td>object</td>
			<td><pre lang="json">
{
  "accessModes": [
    "ReadWriteOnce"
  ],
  "annotations": {},
  "dataSource": {},
  "enabled": true,
  "existingClaim": "",
  "labels": {},
  "selector": {},
  "size": "1Gi",
  "storageClass": ""
}
</pre>
</td>
			<td>Volume persistence settings.</td>
		</tr>
		<tr>
			<td>persistence.accessModes</td>
			<td>list</td>
			<td><pre lang="json">
[
  "ReadWriteOnce"
]
</pre>
</td>
			<td>The volume access modes, some of "ReadWriteOnce", "ReadOnlyMany", "ReadWriteMany", "ReadWriteOncePod".  "ReadWriteOnce" => The volume can be mounted as read-write by a single node. ReadWriteOnce access mode still can                    allow multiple pods to access the volume when the pods are running on the same node. "ReadOnlyMany" => The volume can be mounted as read-only by many nodes. "ReadWriteMany" => The volume can be mounted as read-write by many nodes. "ReadWriteOncePod" => The volume can be mounted as read-write by a single Pod. Use ReadWriteOncePod access mode if                       you want to ensure that only one pod across whole cluster can read that PVC or write to it. </td>
		</tr>
		<tr>
			<td>persistence.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Annotations for the PVC.</td>
		</tr>
		<tr>
			<td>persistence.dataSource</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Custom PVC data source.</td>
		</tr>
		<tr>
			<td>persistence.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable data persistence (true) or use temporary storage (false).</td>
		</tr>
		<tr>
			<td>persistence.existingClaim</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Use an already existing claim.</td>
		</tr>
		<tr>
			<td>persistence.labels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Labels for the PVC.</td>
		</tr>
		<tr>
			<td>persistence.selector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Selector to match an existing Persistent Volume (this value is evaluated as a template).  selector:   matchLabels:     app: my-app </td>
		</tr>
		<tr>
			<td>persistence.size</td>
			<td>string</td>
			<td><pre lang="json">
"1Gi"
</pre>
</td>
			<td>The volume size with unit.</td>
		</tr>
		<tr>
			<td>persistence.storageClass</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The (storage) class of PV.</td>
		</tr>
		<tr>
			<td>podAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Pod Annotations. Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/</td>
		</tr>
		<tr>
			<td>podLabels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Pod Labels. Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/</td>
		</tr>
		<tr>
			<td>podSecurityContext</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "fsGroup": 1000,
  "fsGroupChangePolicy": "Always"
}
</pre>
</td>
			<td>Pod Security Context. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/</td>
		</tr>
		<tr>
			<td>podSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>If specified, all processes of the container are also part of the supplementary group.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroupChangePolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td>Change ownership and permission of the volume before being exposed inside a Pod.</td>
		</tr>
		<tr>
			<td>readinessProbe</td>
			<td>object</td>
			<td><pre lang="json">
{
  "failureThreshold": 10,
  "initialDelaySeconds": 15,
  "periodSeconds": 20,
  "successThreshold": 1,
  "tcpSocket": {
    "port": 9979
  },
  "timeoutSeconds": 5
}
</pre>
</td>
			<td>Configure extra options for containers probes.</td>
		</tr>
		<tr>
			<td>readinessProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>readinessProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td>Delay after container start until ReadinessProbe is executed.</td>
		</tr>
		<tr>
			<td>readinessProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>readinessProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>readinessProbe.tcpSocket</td>
			<td>object</td>
			<td><pre lang="json">
{
  "port": 9979
}
</pre>
</td>
			<td>TCP socket configuration for the readiness probe.</td>
		</tr>
		<tr>
			<td>readinessProbe.tcpSocket.port</td>
			<td>int</td>
			<td><pre lang="json">
9979
</pre>
</td>
			<td>Port to check for readiness.</td>
		</tr>
		<tr>
			<td>readinessProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>replicaCount</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Set the amount of replicas of deployment.</td>
		</tr>
		<tr>
			<td>resources</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Configure resource requests and limits. Ref: https://kubernetes.io/docs/user-guide/compute-resources/</td>
		</tr>
		<tr>
			<td>service</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {},
  "clusterIP": "None",
  "enabled": true,
  "ports": {
    "http": {
      "containerPort": 9979,
      "port": 9979,
      "protocol": "TCP"
    }
  },
  "sessionAffinity": "",
  "sessionAffinityConfig": {},
  "type": "ClusterIP"
}
</pre>
</td>
			<td>Define and create Kubernetes Service. Ref.: https://kubernetes.io/docs/concepts/services-networking/service</td>
		</tr>
		<tr>
			<td>service.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations.</td>
		</tr>
		<tr>
			<td>service.clusterIP</td>
			<td>string</td>
			<td><pre lang="json">
"None"
</pre>
</td>
			<td>This creates a headless service. Instead of load balancing, it creates a DNS A record for each pod.</td>
		</tr>
		<tr>
			<td>service.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable kubernetes service creation.</td>
		</tr>
		<tr>
			<td>service.ports</td>
			<td>object</td>
			<td><pre lang="json">
{
  "http": {
    "containerPort": 9979,
    "port": 9979,
    "protocol": "TCP"
  }
}
</pre>
</td>
			<td>Define the ports of Service. You can set the port value to an arbitrary value, it will map the container port by name.</td>
		</tr>
		<tr>
			<td>service.ports.http</td>
			<td>object</td>
			<td><pre lang="json">
{
  "containerPort": 9979,
  "port": 9979,
  "protocol": "TCP"
}
</pre>
</td>
			<td>HTTP port configuration.</td>
		</tr>
		<tr>
			<td>service.ports.http.containerPort</td>
			<td>int</td>
			<td><pre lang="json">
9979
</pre>
</td>
			<td>Internal port.</td>
		</tr>
		<tr>
			<td>service.ports.http.port</td>
			<td>int</td>
			<td><pre lang="json">
9979
</pre>
</td>
			<td>Accessible port.</td>
		</tr>
		<tr>
			<td>service.ports.http.protocol</td>
			<td>string</td>
			<td><pre lang="json">
"TCP"
</pre>
</td>
			<td>service protocol.</td>
		</tr>
		<tr>
			<td>service.sessionAffinity</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Session Affinity for Kubernetes service, can be "None" or "ClientIP" If "ClientIP", consecutive client requests will be directed to the same Pod ref: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies </td>
		</tr>
		<tr>
			<td>service.sessionAffinityConfig</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional settings for the sessionAffinity sessionAffinityConfig:   clientIP:     timeoutSeconds: 300</td>
		</tr>
		<tr>
			<td>service.type</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIP"
</pre>
</td>
			<td>Choose the kind of Service, one of "ClusterIP", "NodePort" or "LoadBalancer".</td>
		</tr>
		<tr>
			<td>serviceAccount</td>
			<td>object</td>
			<td><pre lang="json">
{
  "annotations": {},
  "automountServiceAccountToken": false,
  "create": true,
  "labels": {},
  "name": ""
}
</pre>
</td>
			<td>Configuration for the ServiceAccount used by the application.</td>
		</tr>
		<tr>
			<td>serviceAccount.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Annotations to add to the service account</td>
		</tr>
		<tr>
			<td>serviceAccount.create</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Specifies whether a service account should be created</td>
		</tr>
		<tr>
			<td>serviceAccount.labels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels for the ServiceAccount.</td>
		</tr>
		<tr>
			<td>serviceAccount.name</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The name of the service account to use. If not set and create is true, a name is generated using the fullname template</td>
		</tr>
		<tr>
			<td>startupProbe</td>
			<td>object</td>
			<td><pre lang="json">
{
  "failureThreshold": 10,
  "initialDelaySeconds": 15,
  "periodSeconds": 20,
  "successThreshold": 1,
  "tcpSocket": {
    "port": 9979
  },
  "timeoutSeconds": 5
}
</pre>
</td>
			<td>Configure extra options for containers probes.</td>
		</tr>
		<tr>
			<td>startupProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>startupProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
15
</pre>
</td>
			<td>Delay after container start until StartupProbe is executed.</td>
		</tr>
		<tr>
			<td>startupProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
20
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>startupProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>startupProbe.tcpSocket</td>
			<td>object</td>
			<td><pre lang="json">
{
  "port": 9979
}
</pre>
</td>
			<td>TCP socket configuration for the startup probe.</td>
		</tr>
		<tr>
			<td>startupProbe.tcpSocket.port</td>
			<td>int</td>
			<td><pre lang="json">
9979
</pre>
</td>
			<td>Port to check for startup.</td>
		</tr>
		<tr>
			<td>startupProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>systemExtensions</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Allows to configure the system extensions to load. This is intended for internal usage, prefer to use `extensions` for user configured extensions. This value will override the configuration in `global.systemExtensions`.</td>
		</tr>
		<tr>
			<td>terminationGracePeriodSeconds</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>In seconds, time the given to the pod needs to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods</td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Tolerations for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/</td>
		</tr>
		<tr>
			<td>topologySpreadConstraints</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule</td>
		</tr>
		<tr>
			<td>udmRestApi</td>
			<td>object</td>
			<td><pre lang="json">
{
  "debug": "2",
  "image": {
    "pullPolicy": null,
    "registry": "",
    "repository": "nubus-dev/images/udm-rest-api",
    "tag": "latest"
  },
  "tls": {
    "caCertificateFile": "/certificates/ca.crt",
    "certificateFile": "/certificates/tls.crt",
    "certificateKeyFile": "/certificates/tls.key",
    "enabled": false
  }
}
</pre>
</td>
			<td>Application configuration of the UDM REST API</td>
		</tr>
		<tr>
			<td>udmRestApi.debug</td>
			<td>string</td>
			<td><pre lang="json">
"2"
</pre>
</td>
			<td>The verbosity of log messages. Possible values: 0-4/99 (0: Error, 1: Warn, 2: Info, 3: Debug, 4: Trace, 99: sensitive data like cleartext passwords is logged as well).</td>
		</tr>
		<tr>
			<td>udmRestApi.image</td>
			<td>object</td>
			<td><pre lang="json">
{
  "pullPolicy": null,
  "registry": "",
  "repository": "nubus-dev/images/udm-rest-api",
  "tag": "latest"
}
</pre>
</td>
			<td>Container image configuration.</td>
		</tr>
		<tr>
			<td>udmRestApi.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>udmRestApi.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>udmRestApi.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus-dev/images/udm-rest-api"
</pre>
</td>
			<td>Container image repository.</td>
		</tr>
		<tr>
			<td>udmRestApi.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"latest"
</pre>
</td>
			<td>Container image tag.</td>
		</tr>
		<tr>
			<td>udmRestApi.tls</td>
			<td>object</td>
			<td><pre lang="json">
{
  "caCertificateFile": "/certificates/ca.crt",
  "certificateFile": "/certificates/tls.crt",
  "certificateKeyFile": "/certificates/tls.key",
  "enabled": false
}
</pre>
</td>
			<td>TLS configuration for LDAP connections.</td>
		</tr>
		<tr>
			<td>udmRestApi.tls.caCertificateFile</td>
			<td>string</td>
			<td><pre lang="json">
"/certificates/ca.crt"
</pre>
</td>
			<td>Path the CA certificate file (TLSCACertPath (slapd), CA_CERT_FILE(entrypoint))</td>
		</tr>
		<tr>
			<td>udmRestApi.tls.certificateFile</td>
			<td>string</td>
			<td><pre lang="json">
"/certificates/tls.crt"
</pre>
</td>
			<td>Path the servers certificate file</td>
		</tr>
		<tr>
			<td>udmRestApi.tls.certificateKeyFile</td>
			<td>string</td>
			<td><pre lang="json">
"/certificates/tls.key"
</pre>
</td>
			<td>Path the servers private-key file</td>
		</tr>
		<tr>
			<td>udmRestApi.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Enable TLS for LDAP connection.</td>
		</tr>
		<tr>
			<td>updateStrategy</td>
			<td>object</td>
			<td><pre lang="json">
{
  "type": "RollingUpdate"
}
</pre>
</td>
			<td>Set up update strategy. Ref: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy  Example: updateStrategy:  type: RollingUpdate  rollingUpdate:    maxSurge: 25%    maxUnavailable: 25%</td>
		</tr>
		<tr>
			<td>updateStrategy.type</td>
			<td>string</td>
			<td><pre lang="json">
"RollingUpdate"
</pre>
</td>
			<td>Set to Recreate if you use persistent volume that cannot be mounted by more than one pods to make sure the pods are destroyed first.</td>
		</tr>
		<tr>
			<td>waitForDependency</td>
			<td>object</td>
			<td><pre lang="json">
{
  "extraEnvVars": [],
  "extraVolumeMounts": [],
  "extraVolumes": [],
  "image": {
    "pullPolicy": null,
    "registry": null,
    "repository": "nubus/images/wait-for-dependency",
    "tag": "0.35.27@sha256:3f9f37e224a7a8e268ee2cdf1ca8d18826d2d0d5b356a2a5a3cbfa4968a2a281"
  }
}
</pre>
</td>
			<td>Configuration for the wait-for-dependency init container.</td>
		</tr>
		<tr>
			<td>waitForDependency.extraEnvVars</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Array with extra environment variables to add to containers.</td>
		</tr>
		<tr>
			<td>waitForDependency.extraVolumeMounts</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumeMounts.</td>
		</tr>
		<tr>
			<td>waitForDependency.extraVolumes</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumes.</td>
		</tr>
		<tr>
			<td>waitForDependency.image</td>
			<td>object</td>
			<td><pre lang="json">
{
  "pullPolicy": null,
  "registry": null,
  "repository": "nubus/images/wait-for-dependency",
  "tag": "0.35.27@sha256:3f9f37e224a7a8e268ee2cdf1ca8d18826d2d0d5b356a2a5a3cbfa4968a2a281"
}
</pre>
</td>
			<td>Container image configuration.</td>
		</tr>
		<tr>
			<td>waitForDependency.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>waitForDependency.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>waitForDependency.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"nubus/images/wait-for-dependency"
</pre>
</td>
			<td>Container image repository.</td>
		</tr>
		<tr>
			<td>waitForDependency.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"0.35.27@sha256:3f9f37e224a7a8e268ee2cdf1ca8d18826d2d0d5b356a2a5a3cbfa4968a2a281"
</pre>
</td>
			<td>Container image tag.</td>
		</tr>
	</tbody>
</table>

