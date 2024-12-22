from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Create MetaData object
metadata = MetaData()

# Define the base
base_model = declarative_base(metadata=metadata)