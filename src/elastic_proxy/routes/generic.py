from typing import Any, Dict

from elastic_transport import ApiResponse
from elasticsearch import Elasticsearch, NotFoundError, RequestError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from ..elastic_client import get_elasticsearch_client
from ..logger import log_info
from ..utils.auth import validate_private_key

router = APIRouter(prefix="/generic", tags=["Generic Elasticsearch Actions"])


@router.get(
    "/ping",
    summary="Ping Elasticsearch Cluster",
    description="""# Check if the connection to the Elasticsearch cluster is active and responsive.
        This endpoint sends a simple ping request to the Elasticsearch cluster to verify its availability.
        It does not require any additional parameters or headers beyond the `PRIVATE-KEY`.
        Use Case:
        - Verify that the Elasticsearch cluster is up and running.
        - Test the connectivity between the proxy and the Elasticsearch cluster.
    """
)
async def ping_elasticsearch(request: Request, _: None = Depends(validate_private_key)):
    """Vérifie que la connexion à Elasticsearch fonctionne."""
    client: Elasticsearch = get_elasticsearch_client()
    try:
        return client.ping()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion à Elasticsearch : {str(e)}")


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
async def generic_elasticsearch_request(
    request: Request,
    path: str,
    _: None = Depends(validate_private_key),
) -> JSONResponse:
    client: Elasticsearch = get_elasticsearch_client()

    # Récupérer la méthode HTTP (GET, POST, PUT, DELETE, etc.)
    method: str = request.method

    # Récupérer le corps de la requête (si présent)
    body = None
    if method in ["POST", "PUT"]:
        body = await request.json()

    # Récupérer les paramètres de requête (query string)
    params: Dict[str, str] = dict(request.query_params)

    log_info("method=%s" % method)
    log_info("path=/%s" % path)
    log_info("body=%s" % body)
    log_info("params=%s" % params)
    log_info("request.headers=%s" % request.headers)

    headers: Dict[str, str] = dict(request.headers)
    headers.pop("host", None)
    headers.pop("user-agent", None)
    headers.pop("accept", None)
    headers.pop("private-key", None)
    headers.pop("content-length", None)
    headers.pop("content-type", None)
    # if "content-type" not in headers:
    headers.update(
        {
            "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
            "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
        }
    )
    log_info("headers=%s" % headers)

    try:
        # Utiliser perform_request avec method et target (None pour cibler un nœud aléatoire)
        response: ApiResponse[Any] = client.perform_request(
            method=method,
            path=f"/{path}",
            body=body,
            headers=headers
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
