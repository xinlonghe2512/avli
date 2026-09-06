from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


async def process_and_ingest(raw_text: str, _source_url: str) -> None:
    # 1. Chunk document
    chunks = text_splitter.split_text(raw_text)

    if not chunks:
        return

    # 2. Generate embeddings & upsert to your vector DB
    # Example logic:
    # embeddings = await model.aencode(chunks)
    # await vector_client.upsert(
    #     collection="web_corpus",
    #     documents=chunks,
    #     embeddings=embeddings,
    #     metadata=[{"url": source_url} for _ in chunks]
    # )
    # print(f"Ingested {len(chunks)} chunks from: {source_url}")
