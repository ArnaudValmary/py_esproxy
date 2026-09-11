from typing import AsyncGenerator

from elasticsearch import AsyncElasticsearch, Elasticsearch

from .config import settings


def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(
        hosts=[settings.ELASTIC_HOST],
        basic_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
        ca_certs=settings.ELASTIC_CERT_PATH if settings.ELASTIC_CERT_PATH else None,
        verify_certs=True if settings.ELASTIC_CERT_PATH else False,
    )


async def get_async_elasticsearch_client() -> AsyncGenerator[AsyncElasticsearch]:
    client = AsyncElasticsearch(
        hosts=[settings.ELASTIC_HOST],
        basic_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
        ca_certs=settings.ELASTIC_CERT_PATH if settings.ELASTIC_CERT_PATH else None,
        verify_certs=True if settings.ELASTIC_CERT_PATH else False,
    )
    try:
        yield client
    finally:
        await client.close()
