from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import registry

# Create MetaData object
mapper_registry = registry()
metadata = mapper_registry.metadata

# Define the base
base_model = declarative_base(metadata=metadata)