import csv
from datetime import datetime
import logging

import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.redis import Redis

from src.common.config import REDIS_CFG
from src.common.utils import generate_redis_connection_string, get_filename_without_extension


def csv_loader_task(filename):
    conn = redis.StrictRedis(host=REDIS_CFG["host"], port=REDIS_CFG["port"], password=REDIS_CFG["password"])

    # Create a new index, named by CSV file and datetime
    index_name = f"minipilot_rag_{get_filename_without_extension(filename)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_idx"
    index_schema = None
    vector_schema = {
        "algorithm": "HNSW"
    }

    """
    # Use index_schema if you would like to index other fields. Not used by semantic search but for hybrid search if required
    index_schema = {
        "tag": [{"name": "genre"},
                {"name": "country"}],
        "text": [{"name": "names"}],
        "numeric": [{"name": "revenue"},
                    {"name": "score"},
                    {"name": "date_x"}]
    }
    """

    # Validate there is an OPENAI_API_KEY passed in the environment
    try:
        embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    except Exception as e:
        logging.error(e)

    # If there is no index for RAG, this is the first index; then, the user should make it current from the UI
    try:
        conn.ft('minipilot_rag_alias').info()
    except redis.exceptions.ResponseError as e:
        logging.warning(f"No alias exists for semantic search. Associate the alias to the desired index")

    # https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    # the default model is "text-embedding-ada-002".
    # max input is 8191 tokens
    # 1 token ~= 4 chars in English
    # 8191 x 4 = 32764 maximum characters that can be represented by a vector embedding
    # choosing 10000 as chunk size seems ok
    doc_splitter = RecursiveCharacterTextSplitter(  chunk_size=10000,
                                                    chunk_overlap=50,
                                                    length_function=len,
                                                    add_start_index=True
                                                    )

    # There may be many strategies to index a CSV, for the benefit of simplicity,
    # here we convert a dictionary to a string representation where each key-value pair is on a separate line and formatted as key: value
    with open(filename, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:
            row_str = '\n'.join([f"{key}: {value}" for key, value in row.items()])
            splits = doc_splitter.split_text(row_str)
            metadatas = None

            """
            # If there is a index_schema defined, add metadata here
            unix_timestamp = int(datetime.strptime(row['date_x'].strip(), "%m/%d/%Y").timestamp())
            metadatas = {"names": row['names'],
                         "genre": row['genre'],
                         "country": row['country'],
                         "revenue": row['revenue'],
                         "score": row['score'],
                         "date_x": unix_timestamp}
                         
            metadatas=[metadatas] * len(splits),
            """

            if len(splits) > 0:
                # Ingest the document
                Redis.from_texts(texts=splits,
                                 metadatas=metadatas,
                                 embedding=embedding_model,
                                 index_name=index_name,
                                 index_schema=index_schema,
                                 vector_schema=vector_schema,
                                 redis_url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]))

