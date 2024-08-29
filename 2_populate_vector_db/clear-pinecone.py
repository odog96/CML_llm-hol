# clear pine cone db
from pinecone import Pinecone, ServerlessSpec

PINECONE_INDEX = os.getenv('PINECONE_INDEX')

pc.delete_index(name=PINECONE_INDEX)