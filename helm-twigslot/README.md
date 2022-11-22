# Instructions

## Secrets
```
k apply -f kubernetes/secrets/cloudflare-credentials.yaml
```
```
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-credentials
type: Opaque
stringData:
  email: <cloudflare email>
  apiKey: <cloudflare apikey>
```
## Helm

This is just a rough guide (mainly for the author himself)
```
cd helm-twigslot
# helm repo add ory https://k8s.ory.sh/helm/charts
helm repo update
# helm dependency list
helm dependency update
helm install -f custom-values.yaml blueberry .
```
Replace `blueberry` with whatever you want to name it.

## Networking
Kubernetes Ingress is a PITA to setup locally... commonly people run into `<pending> External IP`  issues.

I might try proxmox in future, but for now I just use civo. It's the cheapest that comes with a LB.

## Traefik
```
kubectl port-forward $(kubectl get pods --selector "app.kubernetes.io/name=traefik" --output=name) 9000:9000
```
Dashboard will be at `localhost:9000/dashboard`

## Kratos
There are 