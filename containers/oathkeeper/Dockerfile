FROM oryd/oathkeeper:v0.39.3
ADD ./containers/oathkeeper/config.yaml /config.yaml
ADD ./containers/traefik/rules.json /rules.json
ENTRYPOINT [ "oathkeeper", "serve", "--config", "/config.yaml" ]
# ADD ./containers/jwks.json /jwks.json