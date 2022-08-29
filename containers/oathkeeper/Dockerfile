FROM oryd/oathkeeper:v0.39.3
ADD ./containers/oathkeeper/config.yaml /config.yaml
ADD ./containers/oathkeeper/rules.json /rules.json
ADD ./containers/oathkeeper/jwks.json /jwks.json
ENTRYPOINT [ "oathkeeper", "serve", "--config", "/config.yaml" ]