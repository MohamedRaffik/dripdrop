import asyncio
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse, urlunparse

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.settings import settings

_client = boto3.client(
    "s3",
    endpoint_url=settings.aws_endpoint_url,
    region_name=settings.aws_region_name,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    config=Config(s3={"addressing_style": "virtual"}),
)


def resolve_url(filename: str):
    url = urlparse(urljoin(settings.aws_endpoint_url, filename))
    netloc = f"{settings.aws_s3_bucket}.{url.netloc}"
    return urlunparse(
        [url.scheme, netloc, url.path, url.params, url.query, url.fragment]
    )


async def generate_presigned_upload_url(
    filename: str,
    content_type: str,
    expires_in: int = 3600,
    acl: str = "public-read",
):
    return await asyncio.to_thread(
        _client.generate_presigned_url,
        "put_object",
        Params={
            "Bucket": settings.aws_s3_bucket,
            "Key": filename,
            "ContentType": content_type,
            "ACL": acl,
        },
        ExpiresIn=expires_in,
    )


async def download_file(filename: str) -> bytes:
    def _download():
        response = _client.get_object(
            Bucket=settings.aws_s3_bucket,
            Key=filename,
        )
        return response["Body"].read()

    return await asyncio.to_thread(_download)


async def object_exists(filename: str):
    try:
        await asyncio.to_thread(
            _client.head_object,
            Bucket=settings.aws_s3_bucket,
            Key=filename,
        )
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise


async def copy_file(
    source_key: str,
    dest_key: str,
    acl: str = "public-read",
):
    return await asyncio.to_thread(
        _client.copy_object,
        Bucket=settings.aws_s3_bucket,
        CopySource={"Bucket": settings.aws_s3_bucket, "Key": source_key},
        Key=dest_key,
        ACL=acl,
    )


async def upload_file(
    filename: str,
    body: bytes,
    content_type: str,
    acl="public-read",
):
    return await asyncio.to_thread(
        _client.put_object,
        Bucket=settings.aws_s3_bucket,
        Key=filename,
        Body=body,
        ACL=acl,
        ContentType=content_type,
    )


async def delete_file(filename: str):
    return await asyncio.to_thread(
        _client.delete_object, Bucket=settings.aws_s3_bucket, Key=filename
    )


async def delete_objects_older_than(prefix: str, max_age: timedelta) -> list[str]:
    cutoff = datetime.now(timezone.utc) - max_age

    def _delete_older():
        deleted: list[str] = []
        continuation_token = ""
        while True:
            params = {"Bucket": settings.aws_s3_bucket, "Prefix": prefix}
            if continuation_token:
                params["ContinuationToken"] = continuation_token
            response = _client.list_objects_v2(**params)
            for obj in response.get("Contents", []):
                last_modified = obj["LastModified"]
                if last_modified.tzinfo is None:
                    last_modified = last_modified.replace(tzinfo=timezone.utc)
                if last_modified < cutoff:
                    key = obj["Key"]
                    _client.delete_object(
                        Bucket=settings.aws_s3_bucket,
                        Key=key,
                    )
                    deleted.append(key)
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken", "")
        return deleted

    return await asyncio.to_thread(_delete_older)


async def list_filenames(prefix: str = ""):
    continuation_token = ""
    while True:
        params = {"Bucket": settings.aws_s3_bucket}
        if prefix:
            params["Prefix"] = prefix
        if continuation_token:
            params["ContinuationToken"] = continuation_token
        response = await asyncio.to_thread(_client.list_objects_v2, **params)
        objects: list[str] = list(
            map(lambda object: object["Key"], response.get("Contents", []))
        )
        yield objects
        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken", "")
