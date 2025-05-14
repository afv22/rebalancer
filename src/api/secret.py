import os

from google.cloud import secretmanager


class GoogleSecretWrapper:
    _client = None
    _pid = None

    @classmethod
    def get_secret(cls, secret_name: str):
        if cls._client is None:
            cls._client = secretmanager.SecretManagerServiceClient()

        if cls._pid is None:
            cls._pid = os.environ.get("GOOGLE_PROJECT_ID")

        try:
            secret_name = f"projects/{cls._pid}/secrets/{secret_name}/versions/latest"
            response = cls._client.access_secret_version(request={"name": secret_name})
            return response.payload.data.decode("UTF-8")

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
