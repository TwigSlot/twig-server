# twig_server

## Development Setup
```shell
git clone https://github.com/twigslot/twig-server
cd twig-server
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