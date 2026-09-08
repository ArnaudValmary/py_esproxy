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
poetry run python src/main.py
```

## Show proxy log

```bash
tail -f proxy.log
```

## Tests

### Ping

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000" \
    --header "action: ping" \
    --header "index_name: the_index_name" \
| jq
```

### List predefined actions

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000" \
    --header "action: actions" \
| jq
```

### List Elasticsearch database indices

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000" \
    --header "action: indices_list" \
| jq
```

### Index mapping

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000" \
    --header "action: index_mapping"
    --header "index_name: the_index_name" \
| jq
```

### Empty ES query

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000" \
| jq
```

### Create document

```bash
curl \
    -X POST \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2db" \
    --url "http://localhost:8000/the_index_name/_doc/1" \
    --data '{
        "champ1": "valeur1",
        "champ2": "valeur2"
    }' \
| jq
```

### Sample ES query

```bash
curl \
    -X GET \
    --header "PRIVATE-KEY: 712bfe268bba280cb04c896929bad2d" \
    --url "http://localhost:8000/the_index_name/_mapping" \
| jq
```
