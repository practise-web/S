from core.pipeline import SemanticSearchPipeline
import argparse

def main():
    parser = argparse.ArgumentParser(description="Testing similarity search pipeline")
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help= "path to input PDF file"
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help= "search query"
    )

    args = parser.parse_args()

    pipeline = SemanticSearchPipeline()
    pipeline.add_pdf(args.pdf)

    similar_docs = pipeline.search(args.query)
    if similar_docs:
        print("\nQuery:\n")
        print(args.query)
        print("\nTop result:\n")
        print(similar_docs[0].page_content)
    else:
        print("No documents found.")


if __name__ == "__main__":
    main()