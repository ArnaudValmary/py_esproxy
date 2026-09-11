# py_esproxy

This is an experimental Elasticsearch proxy written in Python

## Docker for an Elasticseach database instance

```bash
docker run \
    --rm \
    --name elasticsearch_container \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=true" \
    -e "ELASTIC_PASSWORD=myespassword" \
    docker.elastic.co/elasticsearch/elasticsearch:8.19.20
```

## Run Elasticsearch proxy

```bash
poetry run uvicorn src.elastic_proxy.main:app --reload
```

## Show proxy log

```bash
tail -f proxy.log
```

## Proxy swagger

[http://localhost:8000/swagger](http://localhost:8000/swagger)

## Tests

### Ping

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000/generic/ping" \
| jq
```

### List Elasticsearch database indices

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000/predefined/indices_list" \
| jq
```

### Index mapping

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000/predefined/index_mapping" \
    --header "index-name: my_new_index" \
| jq
```

### Empty ES query

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000/generic/" \
| jq
```

### Create document

```bash
curl \
    -X POST \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000/generic/the_index_name/_doc/1" \
    --data '{
        "field1": "value1",
        "field2": "value2"
    }' \
| jq
```

### Sample ES query

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2d" \
    --url "http://localhost:8000/generic/the_index_name/_mapping"  \
| jq
```
