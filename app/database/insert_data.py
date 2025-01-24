from connection import ensure_database_exists, setup_database_and_tables
from sqlalchemy.orm import sessionmaker

host = "localhost"
port = 5432
user = "postgres"
password = "1234"
database_name = "book_recommend"

ensure_database_exists(host, port, user, password, database_name)
engine = setup_database_and_tables(host, port, user, password, database_name)

Session = sessionmaker(bind=engine)
session = Session()

session.close()