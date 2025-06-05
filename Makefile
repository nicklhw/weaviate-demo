.PHONY: all categorize generate query load help

# Run all scripts in order
all: load query categorize generate image

load:
	uv run create_collection.py

query:
	uv run query_collection.py

categorize:
	uv run categorize.py

generate:
	uv run generation.py

image:
	uv run image_rag.py

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  all         Run all scripts in order: load, query, categorize, generate"
	@echo "  load        Run create_collection.py"
	@echo "  query       Run query_collection.py"
	@echo "  categorize  Run categorize.py"
	@echo "  generate    Run generation.py"
	@echo "  help        Show this help message"