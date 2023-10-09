# Deploying to MicroK8 cluster
These set of notes are more for myself. It isn't as straightforward as a `docker-compose up`. Decent knowledge of Kubernetes will be required.
## Setting kubeconfig
```bash
ssh user@microk8
user$ microk8 config
# copy and paste the output into ~/.kube/config
user$ exit
k config use-context microk8s
k get node
```
## Setting up PV and PVC
```bash
k apply -f kubernetes/config/twig-local-sc.yaml
k apply -f kubernetes/config/twig-local-pv.yaml
k apply -f kubernetes/config/twig-local-pvc.yaml
k describe pvc
```
## Migration of schemas for kratos auth server
Firstly, we need to setup storage class on our microk8 server.
```bash
ssh user@microk8
sudo microk8s enable hostpath-storage
```
Now, log out and we should see a storage class 
```bash
k get sc
k apply -f kubernetes/config/twig-local-pvc.yaml
k get pvc
k apply -f kubernetes/config/configmap-kratos.yaml
k get configmap
k apply -f kubernetes/config/twig-sqlite-migration.yaml
k get pod --watch
# watch until pod "Completed"
```
## Kratos auth service
```bash
# edit nodeport for debugging
vim kubernetes/auth/twig-auth-service.yaml
k apply -f kubernetes/auth/twig-auth-service.yaml
k get svc
```
Go ahead and visit `192.168.1.176:30000` (or whatever `microk8`'s IP is). 
Don't worry about kratos not working for now

## Oathkeeper Deployment
```bash
k apply -f kubernetes/auth/oathkeeper.yaml
```

## Traefik Deployment
There are a few parts to this. 
### Traefik LoadBalancer server
We are using Cloudflare DNS in this case. Expect this to be the hardest step.
```bash
$ k apply -f kubernetes/secrets/cloudflare-secret.yaml
$ k get secret
NAME                TYPE     DATA   AGE
cloudflare-secret   Opaque   1      4m35s
$ vim kubernetes/traefik/traefik-cf-server.yaml
# uncomment nodeports for debugging
$ k apply -f kubernetes/traefik/traefik-cf-server.yaml
```
Visit `192.168.1.176:30004` for the dashboard.
### Traefik IngressRoutes
We can refer to this [guide](https://doc.traefik.io/traefik/user-guides/crd-acme/).
```bash
k apply -f https://raw.githubusercontent.com/traefik/traefik/v2.8/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml
k apply -f https://raw.githubusercontent.com/traefik/traefik/v2.8/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml
k apply -f kubernetes/client/traefik-ingress-client.yaml
k apply -f kubernetes/autofill/traefik-ingress-routes.yaml 
k apply -f kubernetes/traefik/traefik-ingress-routes.yaml
```

### Microk8s Ingress
Because microk8s is self hosted, we need to setup our own ingress controller (for AWS it was conveniently and expensively AWS ELB).
```bash
user$ sudo microk8s enable ingress dns 
user$ exit 
k get ingress
# go comment out the TLS part
vim kubernetes/traefik/traefik-microk8-ingress.yaml
vim kubernetes/traefik/traefik-cf-server.yaml
k apply -f kubernetes/traefik/traefik-microk8-ingress.yaml
k apply -f kubernetes/traefik/traefik-cf-server.yaml
```
check `http://staging.twigslot.com` and subpaths `/twig-api`, `/auth`, `/kratos/health/alive`.
If redirected to https, choose another domain name (caching is annoying).

### TLS for Nginx Ingress
```bash
k apply -f kubernetes/traefik/traefik-letsencrypt.yaml
# check for lets-encrypt-priviate-key
k get secret --all-namespaces
# go uncomment out the TLS part
vim kubernetes/traefik/traefik-microk8-ingress.yaml
vim kubernetes/traefik/traefik-cf-server.yaml
k apply -f kubernetes/traefik/traefik-microk8-ingress.yaml
k apply -f kubernetes/traefik/traefik-cf-server.yaml
```
Wait for a while, then go check `https://staging.twigslot.com`.