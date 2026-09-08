import json
from datetime import datetime
from typing import Dict, Final, Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from config import (
    AUTH_ENABLED,
    ELASTICSEARCH_URL,
    ES_AUTHORIZATION,
    PRIVATE_KEY,
    PROG_NAME,
    PROG_VERSION,
    PROXY_PORT,
)
from logger import log_info, log_request

# Liste des actions prédéfinies autorisées
PREDEFINED_ACTIONS: Final[Dict[str, Dict[str, str]]] = {
    "actions": {},
    "ping": {},
    "indices_list":   {
        "target_path": (
            "_cat/indices" +
            "?h=index,uuid,status,pri,rep,docs.count,docs.delete,store.size,pri.store.size,dataset.size" +
            "&s=index" +
            "&bytes=m" +
            "&format=json"
        )
    },
    "cluster_health": {
        "target_path": "_cluster/health"
    },
    "nodes_list":     {
        "target_path": (
            "_cat/nodes" +
            "?h=name,ip,heap.current,heap.percent,heap.max,ram.percent,cpu,load_1m,load_5m,load_15m,node.role,master" +
            "&s=name" +
            "&bytes=m" +
            "&format=json"
        )
    },
    "stats": {
        "target_path": "_stats"
    },
    "index_mapping":          {
        "target_path": "{index_name}/_mapping"
    },
    "index_stats": {
        "target_path": "{index_name}/_stats"
    },
    "index_settings": {
        "target_path": "{index_name}/_settings"
    },
}


# Exemple d'authentification basique (à adapter)
def check_auth(private_key: str = Header(...)) -> bool:
    if AUTH_ENABLED:
        if private_key != PRIVATE_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return True


app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (à restreindre en production)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les en-têtes
)


# Middleware pour logger les requêtes
@app.middleware("http")
async def log_middleware(request: Request, call_next):
    response = await call_next(request)
    log_request(request.method, request.url.path, response.status_code)
    return response


def get_static_info(action: str) -> Optional[Response]:
    if action == 'actions':
        return Response(
            content=json.dumps(PREDEFINED_ACTIONS),
            status_code=200,
        )
    elif action == 'ping':
        return Response(
            content=json.dumps(
                {
                    'prog': {
                        'name': PROG_NAME,
                        'version': PROG_VERSION,
                    },
                    'date': datetime.now().isoformat(),
                }
            ),
            status_code=200,
        )
    return None


async def call_es(request: Request, path: str, es_headers=Dict[str, str]) -> Response:

    # Construction de l'URL cible
    target_url: str = f"{ELASTICSEARCH_URL}/{path}"

    # Suppression des headers non nécessaires pour Elasticsearch
    es_headers.pop("private-key", None)
    es_headers.pop("host", None)
    es_headers.pop("content-length", None)
    es_headers.pop("user-agent", None)

    # Ajout de l'header pour l'autorisation ES
    es_headers["authorization"] = 'Basic %s' % ES_AUTHORIZATION
    es_headers["content-type"] = "application/json"

    # Récupération des headers et du corps de la requête
    body = await request.body()

    log_info("request headers=%s" % es_headers)

    try:
        # Envoi de la requête à Elasticsearch
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.request(
                method=request.method,
                url=target_url,
                headers=es_headers,
                content=body
            )

            # Retourne la réponse d'Elasticsearch
            # log_info("HEADERS=%s" % response.headers)
            response.headers.pop("content-length", None)
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Proxy vers Elasticsearch
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
async def proxy_to_elasticsearch(request: Request,
                                 path: str,
                                 auth: bool = Depends(check_auth) if AUTH_ENABLED else None) -> Response:

    es_headers: Dict[str, str] = dict(request.headers)

    action: Optional[str] = es_headers.pop("action", None)
    if action:
        response: Optional[Response] = get_static_info(action)
        if response:
            return response

        predefined_action: Optional[Dict[str, str]] = PREDEFINED_ACTIONS.get(action, None)
        if predefined_action:
            path: str = predefined_action.get('target_path', '')
            if "{index_name}" in path:
                index_name: Optional[str] = es_headers.pop("index_name", None)
                if not index_name:
                    raise HTTPException(status_code=400, detail=f"{action} requires index_name headers")
                path = path.replace('{index_name}', index_name)

            log_info(f"Action prédéfinie demandée : {action} -> {path}")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action '{action}'")

    return await call_es(request, path, es_headers)


# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PROXY_PORT)
