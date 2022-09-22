# Useful commands
these references are for myself
```shell
docker-compose -f containers/keto/docker-compose.yml up -d keto keto-init
ssh docker@$(docker-machine ip default) -N -f \
    -L 4466:localhost:4466 \
    -L 4467:localhost:4467
# password is tcuser
curl http://localhost:4466/relation-tuples 
curl http://localhost:4466/relation-tuples/check \
    --data-urlencode "subject_id=cat lady" \
    --data-urlencode "relation=owner" \
    --data-urlencode "namespace=videos" \
    --data-urlencode "object=/cats" \
    -G
curl http://localhost:4466/relation-tuples/check -d @containers/keto/data.json
curl http://localhost:4467/admin/relation-tuples -X PUT -d @containers/keto/data.json
curl http://127.0.0.1:4466/relation-tuples/expand --data-urlencode "namespace=videos" \
    --data-urlencode "relation=owner" \
    --data-urlencode "object=/cats" \
    --data-urlencode "max-depth=3" \
    -G
```
to pretty print json,
```shell
echo '{"a": {"b": "c"}}' | python -m json.tool
```
be careful about the keto version, the documentation (0.9.0) uses different URL endpoints