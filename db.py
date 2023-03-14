import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class Options(Base):
    __tablename__ = "options"

    user_id = sq.Column(sq.Integer)
    option_id = sq.Column(sq.Integer, primary_key=True)


def create_tables(engine):
    Base.metadata.create_all(engine)


load_dotenv()

username = os.getenv('u')
password = os.getenv('pw')
host = os.getenv('h')
port = os.getenv('p')
db_name = os.getenv('db')
DSN = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

engine = sq.create_engine(DSN)
create_tables(engine)
Session = sessionmaker(bind=engine)
sessiondb = Session()
