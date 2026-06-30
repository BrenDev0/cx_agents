import aioboto3
import io


class Aioboto3ObjectStore:
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str
    ):
        self._bucket_name = bucket_name
        self._access_key_id = aws_access_key_id
        self._secret_access_key = aws_secret_access_key
        self._region_name = region_name

    def _client(self):
        session = aioboto3.Session()

        return session.client(
            service_name="s3",
            region_name=self._region_name,
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key
        )

    async def upload(self, key: str, file_bytes: bytes) -> str:
        file_obj = io.BytesIO(file_bytes)

        async with self._client() as s3:
            await s3.upload_fileobj(file_obj, self._bucket_name, key)

        return key

    async def get_object(self, key: str) -> bytes:
        async with self._client() as s3:
            response = await s3.get_object(Bucket=self._bucket_name, Key=key)
            return await response["Body"].read()

    async def delete_object(self, key: str) -> bool:
        async with self._client() as s3:
            await s3.delete_object(Bucket=self._bucket_name, Key=key)

        return True
