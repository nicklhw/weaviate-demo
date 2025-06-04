import os
import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

load_dotenv()

collection_name = "Products"

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_api_key = os.environ["OPENAI_API_KEY"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers={"X-OpenAI-Api-key": openai_api_key},
)


def query_collection():
    print("\n=== Semantic Search ===")
    try:
        client.connect()

        collection = client.collections.get(collection_name)

        queries = [
            "noise cancelling earbuds for travel",
            "shoes for trail running",
            "camera for sports and adventure",
            "workout accessories for home exercise",
        ]

        for query in queries:
            print(f"\nQuery: '{query}'")
            results = collection.query.near_text(query=query, limit=2)
            for obj in results.objects:
                name = obj.properties.get("name", "N/A")
                category = obj.properties.get("category", "N/A")
                print(f"→ {name} (Category: {category})")
    finally:
        client.close()


if __name__ == "__main__":
    query_collection()
