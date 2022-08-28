`docker container ls | grep twig | less -S`
- `less -S` allows for horizontal scrolling

`docker-compose exec <container_name> /bin/sh`
- login to a container to check on files

`docker-compose up --build --force-recreate --no-deps -d reverse-proxy oathkeeper`
- rebuild containers responsible for routing

`docker-compose up --build`
- rebuild all containers
