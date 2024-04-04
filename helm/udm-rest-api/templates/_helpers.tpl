{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
Templates defined in other Helm sub-charts are imported to be used to configure this chart.
If the value .Values.global.nubusDeployment equates to true, the defined templates are imported.
*/}}
{{- define "templates.ldapUri" -}}
{{- if .Values.global.nubusDeployment -}}
{{- $protocol := include "nubusTemplates.ldap.protocol" . -}}
{{- $serviceName := include "nubusTemplates.ldap.serviceName" . | default (printf "%s-ldap-server" .Release.Name) -}}
{{- printf "%s://%s" $protocol $serviceName -}}
{{- else -}}
{{ required "Either .Values.udmRestApi.ldap.uri or .Values.global.ldap.uri must be set" (coalesce .Values.udmRestApi.ldap.uri .Values.global.ldap.uri) }}
{{- end -}}
{{- end -}}

{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "udm-rest-api.configMapUcrDefaults" -}}
{{- $nubusDefaultConfigMapUcrDefaults := printf "%s-stack-data-ums-ucr" .Release.Name -}}
{{- coalesce .Values.configMapUcrDefaults .Values.global.configMapUcrDefaults $nubusDefaultConfigMapUcrDefaults (.Values.global.configMapUcrDefaults | required ".Values.global.configMapUcrDefaults must be defined.") -}}
{{- end -}}

{{- define "udm-rest-api.configMapUcr" -}}
{{- $nubusDefaultConfigMapUcr := printf "%s-stack-data-ums-ucr" .Release.Name -}}
{{- coalesce .Values.configMapUcr .Values.global.configMapUcr $nubusDefaultConfigMapUcr -}}
{{- end -}}

{{- define "udm-rest-api.configMapUcrForced" -}}
{{- coalesce .Values.configMapUcrForced .Values.global.configMapUcrForced "null" -}}
{{- end -}}

{{- define "udm-rest-api.secretRef" -}}
{{- if .Values.udmRestApi.secretRef -}}
secretName: {{ .Values.udmRestApi.secretRef | quote }}
{{- else if .Values.global.nubusDeployment -}}
secretName: {{ printf "%s-udm-rest-api-credentials" .Release.Name | quote }}
{{- else -}}
{{- required ".Values.udmRestApi.secretRef must be defined." .Values.udmRestApi.secretRef -}}
{{- end -}}
{{- end -}}
