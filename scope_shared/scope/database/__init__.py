# TODO: placed here for now, these utility functions need work

def insert(document, db, collection):
    # document["created_at"] = datetime.utcnow()

    inserted = db[collection].insert_one(document)

    return str(inserted.inserted_id)


def find(query, db, collection):
    found = db[collection].find(filter=query)
    found = list(found)
    # To serialize object, convert _id in document to string.
    for doc in found:
        doc.update((k, str(v)) for k, v in doc.items() if k == "_id")

    return found


def find_by_id(id, db, collection):
    # TODO: Check if 'id' is a valid ObjectId, it must be a 12-byte input or a 24-character hex string.
    found = db[collection].find_one({
        "_id": id
    })

    if "_id" in found:
        found["_id"] = str(found["_id"])

    return found
