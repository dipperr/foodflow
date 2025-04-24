from supabase import create_client, Client


class SupabaseSingleton:
    _instance = None

    def __new__(cls, url: str=None, key: str=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = create_client(url, key)
        return cls._instance

    def get_client(self) -> Client:
        return self.client