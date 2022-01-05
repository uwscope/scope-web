import pathlib

from jschon import URI, JSONSchema, create_catalog

schema_dir = pathlib.Path(__file__).parent / "schemas"

catalog = create_catalog("2020-12")

# NOTE: For the subschemas to work, the schemas must be loaded in either "$ref" dependency order, or the base URI-to-directory mapping on the catalog needs to be set up (`.add_directory`) as shown below.

catalog.add_directory(URI("https://uwscope.org/schemas/"), schema_dir)


patient_schema = JSONSchema.loadf(schema_dir / "patient.json")

# TODO: Load other schemas below as API endpoints are added.
values_inventory_schema = JSONSchema.loadf(schema_dir / "values-inventory.json")
identity_schema = JSONSchema.loadf(schema_dir / "identity.json")
