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
    generate_recommendation()
