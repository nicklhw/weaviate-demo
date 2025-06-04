import os
import weaviate
from weaviate.classes.config import Property, DataType, Configure
from dotenv import load_dotenv
from weaviate.classes.init import Auth
import warnings

# Suppressing Pydantic deprecation warning from the weaviate client
warnings.filterwarnings(
    "ignore",
    message="Accessing the 'model_fields' attribute on the instance is deprecated.",
    category=DeprecationWarning,
)

load_dotenv()

collection_name = "Products"

products = [
    {
        "name": "Wireless Noise-Cancelling Headphones",
        "description": "Over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
        "category": "Electronics/Audio",
    },
    {
        "name": "Sports Running Shoes",
        "description": "Lightweight running shoes with breathable mesh and cushioned sole for marathon training.",
        "category": "Apparel/Footwear",
    },
    {
        "name": "4K Action Camera",
        "description": "Rugged waterproof action camera with 4K video recording, ideal for travel and sports.",
        "category": "Electronics/Cameras",
    },
    {
        "name": "Beach Umbrella",
        "description": "Portable beach umbrella, provides UV 50+ production from the sun, include carry bag.",
        "category": "Sports & Outdoors",
    },
    {
        "name": "Bluetooth Earbuds",
        "description": "Compact wireless earbuds with noise isolation and charging case. Great sound quality for music on the go.",
        "category": "Electronics/Audio",
    },
    {
        "name": "Trail Running Sneakers",
        "description": "Durable trail running sneakers with extra grip and ankle support, designed for rough terrains.",
        "category": "Outdoors/Footwear",
    },
    {
        "name": "Ultra HD Underwater Camera",
        "description": "4K Ultra HD action camera. Waterproof and shockproof, perfect for underwater adventures.",
        "category": "Electronics/Cameras",
    },
]

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_api_key = os.environ["OPENAI_API_KEY"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers={"X-OpenAI-Api-key": openai_api_key},
)


def populate_collection():
    print("=== Create Collection ===")

    try:
        client.connect()

        # Delete collection if it exists
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)
            print(f"Collection '{collection_name}' deleted")

        # Create collection
        client.collections.create(
            collection_name,
            properties=[
                Property(
                    name="name", data_type=DataType.TEXT, description="Product name"
                ),
                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    description="Detailed description of the product",
                ),
                Property(
                    name="category",
                    data_type=DataType.TEXT,
                    description="Category label of the product (if known)",
                ),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-large",
                dimensions=1024,
            ),
            generative_config=Configure.Generative.openai(
                model="gpt-4o",
            ),
        )
        print(f"Collection '{collection_name}' created\n")

        collection = client.collections.get(collection_name)

        # Ingest data
        for product in products:
            collection.data.insert(properties=product)
            print(f"Added product: {product['name']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    populate_collection()
