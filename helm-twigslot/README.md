# Instructions

## Starting a DigitalOcean cluster
```
doctl kubernetes cluster create test --count=2 --region=sgp1
k get node
cd kubernetes
```
## Setting up PV and PVC
```bash
doctl compute volume create testvolume1 --region=sgp1 --size=1GiB
# edit twig-do-pv.yaml to have the correct volumeHandle
k apply -f config/twig-do-pv.yaml
k apply -f config/twig-do-pvc.yaml
k describe pvc
```
## Auth
```bash
k apply -f config/configmap-kratos.yaml
k get cm
k apply -f config/twig-sqlite-migration.yaml
k get pod --watch # watch until "Completed"
```

### Kratos & Self-Service
```bash
k apply -f kubernetes/auth/twig-auth-service.yaml
k get svc
k port-forward svc/selfservice-service 4455 # 4455->3000
k port-forward svc/kratos-service 4433
```
Visit `localhost:4455` and one should expect a login page.

Visit `localhost:4433/sessions/whoami` and one should expect
```
{"error":{"code":401,"status":"Unauthorized","reason":"No valid session cookie found.","message":"The request could not be authorized"}}
```
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