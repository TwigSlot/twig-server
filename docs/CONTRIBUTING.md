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
We will assume you have already cloned this repository. Now, move into the directory containing
this repository: `cd twig-server`


We'll now need to configure the environment variables. Run the command below, and see if you are happy
with the defaults (most of you should be).

```bash
cp .env.example .env
```

We'll now start all the dependencies needed to begin working on the project.
