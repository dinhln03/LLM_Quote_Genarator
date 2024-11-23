{{- define "grafana-monitoring.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}
