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
kubectl create ns model-serving
kubens model-serving
cd deployments/hpp
helm upgrade --install hpp .
```