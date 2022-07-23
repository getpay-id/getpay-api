def get_all_active_payment_methods(pg_id: str):
    """
    Tampilkan payment method jika payment gateway diaktifkan
    """
    aggr = [
        {"$match": {"pg_id": pg_id}},
        {
            "$lookup": {
                "from": "payment_channel",
                "let": {"oid": {"$toString": "$_id"}, "status": "$status"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$$status", 1]}}},
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$pm_id", "$$oid"]},
                                    {"$eq": ["$status", 1]},
                                ]
                            }
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "name": "$name",
                            "code": "$unique_code",
                            "fee": "$fee",
                            "fee_percent": "$fee_percent",
                            "img": "$img",
                        }
                    },
                ],
                "as": "channels",
            }
        },
        {
            "$project": {
                "_id": 0,
                "name": "$name",
                "code": "$code",
                "channels": "$channels",
            }
        },
        {"$match": {"$expr": {"$gte": [{"$size": "$channels"}, 1]}}},
    ]
    return aggr
