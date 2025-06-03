import os
import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType, Configure
from dotenv import load_dotenv
from weaviate.connect import ConnectionParams
from weaviate.classes.init import AdditionalConfig, Timeout, Auth
from weaviate.classes.query import Filter
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


def auto_categorization():
    print("\n=== Auto Categorization ===")

    try:
        client.connect()

        collection = client.collections.get(collection_name)

        # Define the new product
        new_product = {
            "name": "Wide Brim Sun Hat",
            "description": "Lightweight and travel-friendly sun hat, ideal for fishing, hiking, hunting, and other outdoor activities.",
            "category": "",  # To be auto-categorized
        }

        print("\n--Adding new product--")
        print(f"Name: {new_product['name']}")
        print(f"Description: {new_product['description']}")
        print(f"Category: {new_product['category']}")

        # Perform a hybrid search (vector + keyword) to find the most similar existing product
        print("\n--Search for most similar product--")
        response = collection.query.hybrid(query=new_product["description"], limit=1)

        # Assign the category from the most similar product
        if response.objects:
            most_similar = response.objects[0]
            inferred_category = most_similar.properties.get("category", "Unknown")
            print("Most similar product found:")
            print(f"\nName: {most_similar.properties.get('name')}")
            print(f"Description: {most_similar.properties.get('description')}")
            print(f"Category: {most_similar.properties.get('category')}")
            new_product["category"] = inferred_category
        else:
            print("No similar product found to infer category.")
            new_product["category"] = "Unknown"

        # Insert the new product into the collection
        print(f"\nAdd {new_product['name']} to cateogry: {new_product['category']}")
        collection.data.insert(properties=new_product)
    finally:
        client.close()


def generate_recommendation():
    print("\n=== Generate Recommendations and Product Description ===")

    try:
        client.connect()

        collection = client.collections.get(collection_name)

        generate_prompt = "Write a one-sentence description for the product: {name}. "
        question = "What running shoes would you recommend for rough terrain?"

        response = collection.generate.bm25(
            query="Running shoes",
            limit=3,
            grouped_task=question,
            single_prompt=generate_prompt,
        )

        print("\n-- Question ---")
        print(question)

        print("\n--- Recommendations ---")
        print(response.generative.text)
        print("\n--- Recommended Products ---\n")
        for o in response.objects:
            print(f"Name: {o.properties['name']}")
            print(f"Description: {o.properties['description']}")
            print(f"Generated Description: {o.generative.text}")
            print("-" * 40)
    finally:
        client.close()


if __name__ == "__main__":
    populate_collection()
    query_collection()
    auto_categorization()
    generate_recommendation()
