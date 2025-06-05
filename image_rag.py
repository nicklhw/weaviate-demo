import os
import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth
import base64
import requests
from weaviate.classes.generate import GenerativeConfig, GenerativeParameters

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
    print("\n=== Rag with Image ===")

    try:
        client.connect()

        collection = client.collections.get(collection_name)

        src_img_path = (
            "https://upload.wikimedia.org/wikipedia/commons/8/8e/YosemiteValley1.png"
        )
        base64_image = base64.b64encode(requests.get(src_img_path).content).decode(
            "utf-8"
        )

        prompt = GenerativeParameters.grouped_task(
            prompt="Which shoes should I wear for the environment in this image?",
            images=[
                base64_image
            ],  # A list of base64 encoded strings of the image bytes
        )

        response = collection.generate.near_text(
            query="Shoes",
            limit=2,
            grouped_task=prompt,
            generative_provider=GenerativeConfig.openai(max_tokens=1000),
        )

        print("\n--- Found Products ---")
        for o in response.objects:
            print(f"Name: {o.properties['name']}")

        print("\n--- Recommendation ---")
        print(response.generative.text)
    finally:
        client.close()


if __name__ == "__main__":
    generate_recommendation()
