`docker container ls | grep twig | less -S`
- `less -S` allows for horizontal scrolling

`docker-compose exec <container_name> /bin/sh`
- login to a container to check on files

`docker-compose up --build --force-recreate --no-deps -d reverse-proxy oathkeeper`
- rebuild containers responsible for routing

`docker-compose up --build`
- rebuild all containers

`flask -A twig_server.app:create_app run --host 0.0.0.0 --port 5001`
Runs flask server on 5001 specifically and on all ports to get around the stupid CORS issue