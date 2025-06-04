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
        print(f"\nAdd {new_product['name']} to category: {new_product['category']}")
        collection.data.insert(properties=new_product)
    finally:
        client.close()


if __name__ == "__main__":
    auto_categorization()
