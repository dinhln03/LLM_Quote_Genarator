# Install ECK operator
kubens observability
kubectl delete -f https://download.elastic.co/downloads/eck/2.13.0/crds.yaml
kubectl create -f https://download.elastic.co/downloads/eck/2.13.0/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/2.13.0/operator.yaml
# Install ngnix ingress controler
# helm upgrade --install ingress-nginx ingress-nginx \
#   --repo https://kubernetes.github.io/ingress-nginx \
#   --namespace ingress-nginx --create-namespace
# Install elk stack
kubectl get serviceaccount filebeat -n elk &> /dev/null && kubectl delete serviceaccount filebeat -n elk || true
kubectl get clusterrolebinding filebeat -n elk &> /dev/null && kubectl delete clusterrolebinding filebeat -n elk || true
kubectl get clusterrole filebeat -n elk &> /dev/null && kubectl delete clusterrole filebeat -n elk || true
yq e '.ingress.hosts = [{"hosts": env(HOST), "path": "/kibana"}]' -i ./charts/eck-kibana/values.yaml
helm upgrade --install elk -f values.yaml .

Username: elastic
Password: kubectl get secret elasticsearch-es-elastic-user -n observability -o jsonpath='{.data.elastic}' | base64 -d