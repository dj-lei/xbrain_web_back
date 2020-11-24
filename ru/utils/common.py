def query_dict(key, value):
    doc = {
        "query": {
            "term": {
                key: str.lower(value)
            }
        }
    }
    return doc