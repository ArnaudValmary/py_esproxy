from elasticsearch import NotFoundError, RequestError
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from ..elastic_client import get_elasticsearch_client
from ..utils.auth import validate_private_key

router = APIRouter(prefix="/predefined", tags=["Predefined Actions"])


@router.get(
    "/indices_list",
    summary="List Elasticsearch Indices",  # Titre court pour SwaggerUI
    description="""# Retrieve a detailed list of all indices in the Elasticsearch cluster.
        Parameters included in the response:
        - index: Name of the index.
        - uuid: Unique identifier for the index.
        - status: Current status of the index (e.g., open, closed).
        - pri: Number of primary shards.
        - rep: Number of replica shards.
        - docs.count: Number of documents in the index.
        - docs.delete: Number of deleted documents in the index.
        - store.size: Total storage size of the index in MB.
        - pri.store.size: Storage size of primary shards in MB.
        - dataset.size: Total size of the dataset (including replicas) in MB.

        Query Parameters:
        - `h`: Fields to include in the response.
        - `s`: Sort by index name.
        - `bytes`: Format storage sizes in megabytes (m).
        - `format`: Return results in JSON forma
    """
)
async def indices_list(request: Request,
                       _: None = Depends(validate_private_key)) -> JSONResponse:
    return get_elasticsearch_request(
        request=request,
        path="_cat/indices" +
        "?h=index,uuid,status,pri,rep,docs.count,docs.delete,store.size,pri.store.size,dataset.size" +
        "&s=index" +
        "&bytes=m" +
        "&format=json"
    )


@router.get(
    "/nodes_list",
    summary="List Elasticsearch Nodes",
    description="""# Retrieve a detailed list of all nodes in the Elasticsearch cluster.
        Parameters included in the response:
        - name: Node name.
        - ip: Node IP address.
        - heap.current: Current heap usage in MB.
        - heap.percent: Percentage of heap used.
        - heap.max: Maximum heap size in MB.
        - ram.percent: Percentage of RAM used.
        - cpu: CPU usage percentage.
        - load_1m, load_5m, load_15m: Load averages for 1, 5, and 15 minutes.
        - node.role: Role of the node (e.g., master, data, ingest).
        - master: Indicates if the node is the master node.

        Query Parameters:
        - `h`: Fields to include in the response.
        - `s`: Sort by node name.
        - `bytes`: Format heap sizes in megabytes (m).
        - `format`: Return results in JSON format.
    """
)
async def nodes_list(request: Request,
                     _: None = Depends(validate_private_key)) -> JSONResponse:
    return get_elasticsearch_request(
        request=request,
        path="_cat/nodes" +
        "?h=name,ip,heap.current,heap.percent,heap.max,ram.percent,cpu,load_1m,load_5m,load_15m,node.role,master" +
        "&s=name" +
        "&bytes=m" +
        "&format=json"
    )


@router.get(
    "/cluster_health",
    summary="Get Elasticsearch Cluster Health",  # Titre court pour SwaggerUI
    description="""# Retrieve the health status of the Elasticsearch cluster.

        This endpoint provides a high-level overview of the cluster's health, including:
        - cluster_name: Name of the Elasticsearch cluster.
        - status: Overall health status of the cluster (e.g., green, yellow, red).
          - green: All primary and replica shards are allocated.
          - yellow: All primary shards are allocated, but some replica shards are not.
          - red: Some primary shards are not allocated.
        - timed_out: Indicates if the request timed out.
        - number_of_nodes: Total number of nodes in the cluster.
        - number_of_data_nodes: Number of data nodes in the cluster.
        - active_primary_shards: Number of active primary shards.
        - active_shards: Total number of active shards (primary + replica).
        - relocating_shards: Number of shards currently being relocated.
        - initializing_shards: Number of shards currently initializing.
        - unassigned_shards: Number of shards that are not assigned to any node.
        - delayed_unassigned_shards: Number of shards whose allocation is delayed.
        - number_of_pending_tasks: Number of pending tasks in the cluster.
        - number_of_in_flight_fetch: Number of ongoing fetch operations.
        - task_max_waiting_in_queue_millis: Maximum time a task has been waiting in the queue.
        - active_shards_percent_as_number: Percentage of active shards.
    """
)
async def cluster_health(request: Request,
                         _: None = Depends(validate_private_key)) -> JSONResponse:
    return get_elasticsearch_request(
        request=request,
        path="_cluster/health"
    )


@router.get(
    "/index_mapping",
    summary="Get Index Mapping",  # Titre court pour SwaggerUI
    description="""# Retrieve the mapping definition of a specific Elasticsearch index.
        The mapping defines the structure of the documents stored in the index, including:
        - Field names: Names of the fields in the index.
        - Data types: Data types of each field (e.g., text, keyword, integer, date, etc.).
        - Analyzers: Custom analyzers applied to text fields.
        - Index settings: Additional settings like `index`, `store`, or `doc_values`.

        Required Header:
        - `index-name`: Name of the Elasticsearch index for which to retrieve the mapping.
    """
)
async def index_mapping(request: Request,
                        index_name: str = Header(..., alias="index-name"),
                        _: None = Depends(validate_private_key)) -> JSONResponse:
    return get_elasticsearch_request(
        request=request,
        path=f"{index_name}/_mapping"
    )


@router.get(
    "/index_settings",
    summary="Get Index Settings",
    description="""# Retrieve the settings of a specific Elasticsearch index.
        The settings define the configuration of the index, including:
        - Number of shards: Number of primary shards (`number_of_shards`).
        - Number of replicas: Number of replica shards (`number_of_replicas`).
        - Refresh interval: How often the index is refreshed (`refresh_interval`).
        - Analysis settings: Custom analyzers, tokenizers, and filters.
        - Routing settings: Shard allocation awareness and routing settings.
        - Other configurations: Additional settings like `max_result_window`, `max_inner_result_window`, etc.

        Required Header:
        - `index-name`: Name of the Elasticsearch index for which to retrieve the settings.
    """
)
async def index_settings(request: Request,
                         index_name: str = Header(..., alias="index-name"),
                         _: None = Depends(validate_private_key)) -> JSONResponse:
    return get_elasticsearch_request(
        request=request,
        path=f"{index_name}/_settings"
    )


@router.get(
    "/index_stats",
    summary="Get Index Statistics",
    description="""# Retrieve the statistics of a specific Elasticsearch index.
        The statistics provide detailed metrics about the index, including:
        - Document count: Total number of documents in the index (`docs.count`).
        - Deleted documents: Number of deleted documents (`docs.deleted`).
        - Storage size: Total storage size of the index (`store.size_in_bytes`).
        - Primary store size: Storage size of primary shards (`store.pri.size_in_bytes`).
        - Shard statistics: Metrics for each shard, including `docs`, `store`, and `indexing`.
        - Indexing statistics: Number of indexing operations, time spent, and latency.
        - Search statistics: Number of search operations, time spent, and latency.
        - Cache statistics: Metrics for request cache, query cache, and field data cache.

        Required Header:
        - `index-name`: Name of the Elasticsearch index for which to retrieve the statistics.
    """
)
async def index_stats(request: Request,
                      index_name: str = Header(..., alias="index-name"),
                      _: None = Depends(validate_private_key)) -> JSONResponse:
    return get_elasticsearch_request(
        request=request,
        path=f"{index_name}/_stats"
    )


def get_elasticsearch_request(
    request: Request,
    path: str,
    _: None = Depends(validate_private_key),
) -> JSONResponse:
    """
    Appel générique vers n'importe quel endpoint Elasticsearch.
    Exemples :
    - GET /generic/_cat/indices
    - POST /generic/my_index/_doc
    - PUT /generic/my_index
    - DELETE /generic/my_index
    """
    client = get_elasticsearch_client()

    # Récupérer la méthode HTTP (GET, POST, PUT, DELETE, etc.)
    method = request.method

    # Récupérer le corps de la requête (si présent)
    body = None
    if method in ["POST", "PUT"]:
        body = request.json()

    # Récupérer les paramètres de requête (query string)
    params: dict[str, str] = dict(request.query_params)

    try:
        # Utiliser perform_request avec method et target (None pour cibler un nœud aléatoire)
        response = client.perform_request(
            method=method,
            path=f"/{path}",
            body=body,
            params=params,
            headers=request.headers,
        )

        # Extraire le contenu brut de la réponse
        if hasattr(response, "body"):
            # Si la réponse a un attribut body (ex: TextApiResponse)
            content = response.body
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            # Essayer de parser en JSON si possible, sinon retourner le texte brut
            try:
                import json
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                pass
            return JSONResponse(content=content)
        else:
            # Si la réponse est déjà un dictionnaire (ex: pour les endpoints comme /_cluster/health)
            return JSONResponse(content=response)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Ressource non trouvée : {str(e)}")
    except RequestError as e:
        raise HTTPException(status_code=400, detail=f"Requête invalide : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
