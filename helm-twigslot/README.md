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
# IMPT: edit twig-do-pv.yaml to have the correct volumeHandle
k apply -f config/twig-do-pv.yaml
k create ns twigslot # create namespace "twigslot"
kubens twigslot
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
k apply -f auth/twig-auth-service.yaml
k get svc
k port-forward svc/selfservice-service 4455 # 4455->3000
k port-forward svc/kratos-service 4433
```
Visit `localhost:4455` and one should expect a login page.

Visit `localhost:4433/sessions/whoami` and one should expect
```
{"error":{"code":401,"status":"Unauthorized","reason":"No valid session cookie found.","message":"The request could not be authorized"}}
```

### Oathkeeper Deployment
```bash
k apply -f config/configmap-oathkeeper.yaml
k apply -f auth/oathkeeper.yaml
```

## Traefik
Deploy the following in the `default` namespace.
```bash
k apply -f secrets/cloudflare-secret.yaml
vim traefik/traefik-cf-server.yaml # - --api.insecure=true
k apply -f traefik/traefik-cf-server.yaml
k get svc
```
Dashboard will be at `<external-ip>:8080/dashboard`

Tip: If you forgot to apply `cloudflare-secret` before creating the service, you can restart by using 
```
k rollout restart deployment/traefik
```
because deleting and applying takes a long time for the LB to spin up.

**BUT** the above will only work for `deployment`, not stateful set. for `statefulset` just delete the `statefulset` and recreate it using 
```
k delete statefulset traefik
k apply -f auth/traefik-cf-server.yaml
```

### Traefik IngressRoutes
We can refer to this [guide](https://doc.traefik.io/traefik/user-guides/crd-acme/).
```bash
k apply -f https://raw.githubusercontent.com/traefik/traefik/v2.9/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml
k apply -f https://raw.githubusercontent.com/traefik/traefik/v2.9/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml
# be careful about namespacing
k apply -f traefik/traefik-ingress-routes.yaml
# if the route doesnt appear in the dashboard, 
# chances are that the service doesn't exist yet
```
Visit `http://<external-ip>/kratos/sessions/whoami` and it should yield 
``` 
{"error":{"code":401,"status":"Unauthorized","reason":"No valid session cookie found.","message":"The request could not be authorized"}}
```
## Domain
Point your domain `staging.twigslot.com` to the external IP of `k get svc traefik`. 

### You are confident of SSL setup
To check if you got a cert, you can do
``` 
k exec -it svc/traefik -- sh 
cat ssl-certs/acme-cloudflare.json 
```
If it is blank, go take a shit, vomit blood, and come back later (patience is key? just wait it out, mine actually appeared soon after).

### You are NOT confident of SSL setup
If you're using cloudflare (I am), ***remember*** to set SSL/TLS to `Flexible` while testing (***don't*** do this in production, lessons were learnt the hard way).

### Testing
Visit `https://staging.twigslot.com/kratos/sessions/whoami` and it should work.

Visit `https://staging.twigslot.com/auth/login` and it should work. For the record, I wasted 4h of my life because I missed out the `/login` so don't be dumb like me.

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

## Kratos
There are 