import os

# SQLALCHEMY_DATABASE_URI = "postgres://postgres:4357@localhost:5432/test"
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
