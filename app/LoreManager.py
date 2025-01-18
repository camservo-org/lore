import os

import openai
from llama_index.core import (Document, StorageContext, VectorStoreIndex,
                              load_index_from_storage)


class LoreManager:
    def __init__(self, persistence_path, api_key=None):
        self.persistence_path = persistence_path
        self.index = self._setup_persistence(persistence_path)
        self.api_key = api_key

    def _setup_persistence(self, persistence_path):
        if os.path.exists(persistence_path):
            storage_context = StorageContext.from_defaults(persist_dir=persistence_path)
            vector_index = load_index_from_storage(storage_context)
        else:
            vector_index = VectorStoreIndex([])
        return vector_index

    def create_region(self, description):
        ## TODO: Ensure this doesn't get re-run too many times.
        ## TODO: Limit the amount of tokens used, without cutting off the response.
        ## TODO: Feed chatgpt information from our LLM so it can consider it as an input when generating.
        """
        Generates a region in the lore realm.
        """
        if not self.api_key:
            raise ValueError("API key is required to use ChatGPT for name generation.")

        prompt = (
            f"Describe a new region in a fantasy world.  This will be one of many regions.  It should have distinct name, weather, flora, and fauna.  It should use the following description as a starting point.\n\n"
            f"Description: {description if description else 'No description provided.'}"
        )
        try:
            openai.api_key = self.api_key
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a generator of lore in a fantasy game.",
                    },
                    {"role": "user", "content": prompt},
                ],
                # max_tokens=50,
            )
            lore = response.choices[0].message.content
            doc = Document(text=lore)

            self.index.insert(doc)
            self.index.storage_context.persist(self.persistence_path)

        except Exception as e:
            print(f"Error generating realm with ChatGPT: {e}")

    def query_lore(self, query):
        query_engine = self.index.as_query_engine()
        response = query_engine.query(query)
        return response.response
