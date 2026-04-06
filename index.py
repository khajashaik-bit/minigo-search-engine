from indexer import index_page

def load_urls(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    return list(set(urls))  # remove duplicates


def main():
    urls = load_urls("urls.txt")

    print(f"Total unique URLs to index: {len(urls)}\n")

    success_count = 0

    for url in urls:
        try:
            index_page(url)
            success_count += 1
        except Exception as e:
            print("Error indexing:", url)
            print("Reason:", e)

    print("\nIndexing completed!")
    print(f"Successfully indexed {success_count} URLs")


if __name__ == "__main__":
    main()