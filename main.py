from indexer import update_index
from repo import Index

# index = repo.Index()

# index.save_document(repo.Document())

# for doc in index.search("python OR java"):
#     print(doc)


Index.clear()
update_index()