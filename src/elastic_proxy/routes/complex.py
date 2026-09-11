import json
from typing import Dict, List, Literal, Union

from elasticsearch import AsyncElasticsearch, Elasticsearch
from elasticsearch.helpers import async_scan, bulk
from fastapi import APIRouter, Depends, Header, Request, Response

from ..elastic_client import get_async_elasticsearch_client, get_elasticsearch_client
from ..logger import log_error, log_info
from ..utils.auth import validate_private_key

router = APIRouter(prefix="/complex", tags=["Complex Actions"])

ES_SCAN_OUTPUT_FORMAT = Literal["native", "bulk", "simple"]


@router.get("/scan")
async def scan_index(request: Request,
                     index_name: str = Header(..., alias="index-name"),
                     page_size: int = Header(1000, alias="page-size"),
                     es_query: Union[str, Dict] = Header(
                         {
                             "query": {
                                 "match_all": {}
                             }
                         },
                         alias="es-query"
                     ),
                     es_scan_output_format: ES_SCAN_OUTPUT_FORMAT = Header("native", alias="es-scan-output-format"),
                     es_scan_id_field_name: str = Header("__id", alias="es-scan-id-field-name"),
                     _: None = Depends(validate_private_key),
                     es_client: AsyncElasticsearch = Depends(get_async_elasticsearch_client)):
    # log_info("SCAN")
    # es_client: AsyncElasticsearch = get_elastic_client(asynchronous=True)
    # log_info("ES client = %s" % client)
    if isinstance(es_query, str):
        es_query = json.loads(es_query)
    # log_info("query=%s" % query)
    if es_scan_output_format == 'native':
        return [
            doc
            async for doc in async_scan(
                client=es_client,
                index=index_name,
                query=es_query,
                size=page_size,
                clear_scroll=True
            )
        ]
    elif es_scan_output_format == 'bulk':
        docs: str = ''.join(
            [
                f"{
                    json.dumps(
                        {
                            "index":
                            {
                                '_index': index_name,
                                '_id': doc.get('_id'),
                            },
                        }
                    )
                }\n{
                    json.dumps(
                        doc.get('_source')
                    )
                }\n"
                async for doc in async_scan(
                    client=es_client,
                    index=index_name,
                    query=es_query,
                    size=page_size,
                    clear_scroll=True
                )
            ]
        )
        return Response(
            content=docs,
            media_type="text/plain",
        )
    elif es_scan_output_format == 'simple':
        docs: str = ''.join(
            [
                f"{
                    json.dumps(
                        (
                            doc['_source'].update(
                                {
                                    es_scan_id_field_name: doc.get('_id')
                                }
                            )
                            or doc['_source']
                        )
                    )
                }\n"
                async for doc in async_scan(
                    client=es_client,
                    index=index_name,
                    query=es_query,
                    size=page_size,
                    clear_scroll=True
                )
            ]
        )
        return Response(
            content=docs,
            media_type="text/plain",
        )


@router.post("/bulk")
async def bulk_update(request: Request,
                      _: None = Depends(validate_private_key),
                      es_client: Elasticsearch = Depends(get_elasticsearch_client)) -> Dict[str, int]:
    operations: List[str] = [
        json.loads(doc)
        for doc in (await request.body()).decode(encoding="utf-8").strip().split("\n")
    ]

    success: bool = True
    failed: str = ""
    try:
        es_client.bulk(
            operations=operations
        )
    except Exception as e:
        log_error(f"Erreur lors de l'appel à bulk: {str(e)}")
        success = False
        failed = [{"error": str(e), "status": 500}]  # Exemple de structure

    es_client.close()

    return Response(
        content=json.dumps(
            {
                "success": success,
                "failed": failed,
            }
        ),
        media_type="application/json",
    )
