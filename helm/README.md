# How-to Guide

## Deploy NGINX-ingress
```shell
kubectl create ns nginx-system
kubens nginx-system
cd nginx-ingress
helm upgrade --install nginx-ingress .
```

## Deploy model
```shell
kubectl create ns quote-gen
kubens model-serving
cd quote_gen_chart
helm upgrade --install quote-gen .
```
