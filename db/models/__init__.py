import logging

from config import App

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register

logger = logging.getLogger(__name__)

engine = create_engine(App.config('POSTGRES_URI'))

DBSession = scoped_session(sessionmaker(bind=engine))
register(DBSession)

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


class Model (Base):
    __abstract__ = True

    query = DBSession.query_property()

    def set_default_attrs(self, **kwargs):
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def add(self):
        DBSession.add(self)
        return self

    def create(self):
        import transaction

        self.add()
        transaction.commit()

    def flush(self):
        DBSession.flush()
        return self

    def save(self):
        import transaction

        self.add()
        transaction.commit()

    def delete(self):
        import transaction

        DBSession.delete(self)
        transaction.commit()

    def __repr__(self):
        return 'Object <{0}. ID:{1}>'.format(self.__class__.__name__, self.id)


from config import App
from db.models.users import *  # noqa: F403


def init(engine):
    DBSession.configure(bind=engine)
    return DBSession
