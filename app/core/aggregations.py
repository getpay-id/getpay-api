def find_duplicate_data(identifier):
    """
    Aggregator untuk menemukan duplikat data dan mengembalikan ID objek.
    """
    aggr = [
        {"$group": {"_id": identifier, "id": {"$first": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$project": {"id": "$id"}},
    ]
    return aggr
