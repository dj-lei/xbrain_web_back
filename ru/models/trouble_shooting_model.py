model = [
    {
        'index': 'trouble-shooting-checklist-images',
        'mappings': {
            "mappings": {
                "properties": {
                    "task_id": {
                        "type": "keyword"
                    },
                    "node_id": {
                        "type": "keyword"
                    },
                    "content": {
                        "type": "object"
                    }
                }
            }
        }
    },
    {
        'index': 'trouble-shooting-checklist-logs',
        'mappings': {
            "mappings": {
                "properties": {
                    "task_id": {
                        "type": "keyword"
                    },
                    "node_id": {
                        "type": "keyword"
                    },
                    "content": {
                        "type": "object"
                    }
                }
            }
        }
    },
]