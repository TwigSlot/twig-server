# twig_server

## Development Setup
```shell
git clone https://github.com/twigslot/twig-server
cd twig-server
cp .env.example .env
docker-compose up -d
```
Note that building the images the first time takes longer, but after docker caches some image layers, the waiting time becomes more bearable.

### Ports in use
Make sure the following ports are free on your host. 

- `3000` for the login/signup UI, currently from [Ory](https://github.com/ory/kratos-selfservice-ui-node/) but will eventually be replaced
- `4433` for [Ory Kratos](https://www.ory.sh/kratos/) API, an identity management system
- `4434` for [Ory Kratos](https://www.ory.sh/kratos/) Admin API, untouched for the most part
- `5000` for the TwigSlot Flask API server, where majority of development will take place
- `7474, 7473, 7687` for a local Neo4J instance (currently unused), though we are currently using Neo4J cloud.

You may use `docker ps` to see the port mappings.

After development, `docker-compose down` to free up cpu resouces and host ports.

## Debugging
In order to debug the Flask api server (`./server.py`) within the docker container or enable hot reload, you can build it with
```shell
docker-compose \
    -f docker-compose.yml \
    -f docker-compose-debug.yml \
    up -d --build --force-recreate server
```

## Errors
### Servers inaccessible on Mac OS
If you're developing on mac, which does not have native docker virtualization support, `http://localhost:3000` and related servers may not be accessible. We will use SSH portforwarding to solve this.

If you run docker on mac using `eval $(docker-machine env default)`, the networking issues are due to the fact that docker containers run inside a virtualbox container. A quick fix for this is to run
```shell
ssh docker@$(docker-machine ip default) -N -f \
    -L 3000:localhost:3000 \
    -L 5000:localhost:5000 \
    -L 5001:localhost:5001 \
    -L 4433:localhost:4433 \
    -L 4434:localhost:4434 \
    -L 4455:localhost:4455
```
A password will be prompted for the virtualbox container, which is `tcuser` by default.

## Deployment (Kubernetes)
This is abit complicated as it involves many moving parts, so this reference is more for myself. You may contact me if you wish to help support deployment.
```shell
docker build -t tch1001/twig_server:v1.1 . \
    -f ./containers/flask/Dockerfile
docker push tch1001/twig_server:v1.1
kubectl apply -f <all the files>
```