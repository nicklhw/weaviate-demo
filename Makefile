.PHONY: all categorize generate query load

# Run all scripts in order
all: load query categorize generate

load:
	uv run create_collection.py

query:
	uv run query_collection.py

categorize:
	uv run categorize.py

generate:
	uv run generation.py