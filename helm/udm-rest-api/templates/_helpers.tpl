{{- /*
SPDX-FileCopyrightText: 2024-2025 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
They are defined so other sub-charts can read information that otherwise would be solely known to this Helm chart.
If compatible Helm charts set .Values.global.nubusDeployment to true, the templates defined here will be imported.
*/}}
{{- define "nubusTemplates.udmRestApi.uri" -}}
{{- printf "http://%s-udm-rest-api:9979/udm/" .Release.Name }}
{{- end -}}

{{- define "nubusTemplates.udmRestApi.host" -}}
{{- printf "%s-udm-rest-api" .Release.Name }}
{{- end -}}

{{- define "nubusTemplates.udmRestApi.port" -}}
9979
{{- end -}}

{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
Templates defined in other Helm sub-charts are imported to be used to configure this chart.
If the value .Values.global.nubusDeployment equates to true, the defined templates are imported.
*/}}
{{- define "udm-rest-api.ldapUri" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.connection.uri" . -}}
{{- else -}}
{{ tpl ( required
  "The LDAP connection has to be configured, see ldap.connection.uri or global.ldap.connection.uri."
  (coalesce .Values.ldap.connection.uri .Values.global.ldap.connection.uri) ) .
}}
{{- end -}}
{{- end -}}

{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "udm-rest-api.configMapUcr" -}}
{{- $nubusConfigMapUcr := printf "%s-stack-data-ums-ucr" .Release.Name -}}
{{- tpl (coalesce .Values.configMapUcr .Values.global.configMapUcr $nubusConfigMapUcr) . -}}
{{- end -}}

{{- define "udm-rest-api.ingress.tls.secretName" -}}
{{- if .Values.ingress.tls.secretName -}}
{{- tpl .Values.ingress.tls.secretName . -}}
{{- else if .Values.global.nubusDeployment -}}
{{- printf "%s-portal-tls" .Release.Name -}}
{{- else -}}
{{- required ".Values.ingress.tls.secretName must be defined" .Values.ingress.tls.secretName -}}
{{- end -}}
{{- end -}}
