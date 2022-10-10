# Contributing to TWIGSLOT

Thank you for your interest in contributing. We appreciate all contributions no matter
how "trivial" they may seem. Please follow the guide below to set up all the dependencies locally and
ensure you have a nice and smooth time.


## System requirements

- Docker (please ensure docker compose is present - it should be by default!)
- Python 3.9.9+ (although older versions should work fine)

Most CPU architectures should work fine. This has been tested on x86/amd64 systems as well as 
arm64 (Apple Silicon) based machines.


## Development environment setup

We will assume you have already cloned this repository. If not, do so with
```bash
git clone https://github.com/twigslot/twig-server.git
```
Now, move into the directory containing this repository: `cd twig-server`

We'll now need to configure the environment variables. Run the command below, and see if you are happy
with the defaults (most of you should be).

```bash
cp .env.dev.example .env
```

We'll now start all the dependencies needed to begin working on the repo.

```bash
docker-compose up -d neo4j kratos oathkeeper mailslurper kratos-selfservice-ui-node
```

> Note: If the above command returns something like: `docker-compose not found`,
> you likely have Compose V2. Replace the `docker-compose` with `docker compose`


### Launching the server locally

Once all the dependencies have started, you can now start the server.
We are using poetry to manage project dependencies.

[Please follow their installation guide here](https://python-poetry.org/docs/#installation)

> Note: You might want to configure poetry to create the virtualenvs within the
> repo directory itself, not scattered around your home. 
> `poetry config virtualenvs.in-project true` should do it.


Next, create a new Python 3.9 virtualenv with `poetry env use 3.9`

> Warning: If you are using a virtualenv manager like pyenv, you might want to set
> `poetry config virtualenvs.prefer-active-python true` so that you can obtain
> the right Python version (3.9)

Now,
```bash
poetry install
```

And you're done! Simply execute `python server.py` in the repo root directory to begin
working on the server.