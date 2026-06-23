from openai import AsyncOpenAI

class OpenaiEmbeddingService:
    def __int__(self, api_key: str, model: str):
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)

    async def embed_query(
        self,
        query: str
    ) -> list[float]:
        response = await self._client.embeddings.create(
            input=query,
            model=self._model
        )

        if not response.data:
            raise ValueError("No embedding data returned from provider")
        
        return response.data[0].embedding


        

