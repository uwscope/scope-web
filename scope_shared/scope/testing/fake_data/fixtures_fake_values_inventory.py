import random

import scope.testing.fake_data.fixtures_fake_life_areas

fake_life_areas = scope.testing.fake_data.fixtures_fake_life_areas.fake_life_areas_factory()

# TODO: still unclear how to handle references

def fake_values_inventory_factory() -> dict:
    fake_values_inventory = {
        "_type": "valuesInventory",
        "_rev": 1,
        "assigned": True,
        # TODO: date pattern needs to be fixed in schema
        "assignedDate": "assignedDate",
        "values": [
            {
                "id": "id",
                "name": "name",
                "dateCreated": "",
                "dateEdited": "",
                # TODO: lifearea seems like inconsistent capitalization
                "lifeareaId": random.choice(list(fake_life_areas.keys())),
                "activities": [
                    {
                        "id": "id",
                        "name": "name",
                        "valueId": "",
                        "dateCreated": "",
                        "dateEdited": "",
                        "lifeareaId": "",
                    },
                    {
                        "id": "id",
                        "name": "name",
                        "valueId": "",
                        "dateCreated": "",
                        "dateEdited": "",
                        "lifeareaId": "",
                    },
                ],
            }
        ],
    }

    return fake_values_inventory
