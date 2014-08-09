__author__ = 'achmed'

import contextlib

from .interface import SampleStorageInterface
from ..sample import GriffinSample
from ..config.configwrapper import ConfigWrapper

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy import event, exc, MetaData, Column, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool
import sqlalchemy.orm.session

import logging
logger = logging.getLogger(__name__)


metadata = MetaData()
base = declarative_base(metadata=metadata, cls=DeferredReflection)


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        logger.info('checkout hook caught a connection error')

        # dispose the whole pool instead of invalidating one at a time
        logger.info('disposing of pool connections')
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


@contextlib.contextmanager
def db_checkout(db):
    dbsession = db()
    yield dbsession
    dbsession.close()


class DBSample(base):
    __tablename__ = 'sample'

    id = Column(Integer, primary_key=True)
    sample = Column(JSON, nullable=False)

    def __init__(self, sample):
        self.sample = sample


class PostgresSampleStorageBackend(SampleStorageInterface):
    def initialize(self, storagecfg):
        cfg = self.cfg = ConfigWrapper(other=storagecfg.get('postgres'))
        self.connstring = cfg.get('connstring', 'postgresql+psycopg2://postgres:postgres@localhost:5432/griffin')
        self.poolrecycle = cfg.getByPath('pool.recycle', 600)
        self.poolsize = cfg.getByPath('pool.size', 2)
        self.sqlecho = cfg.getByPath('sqlecho', False)

        self.engine = create_engine(self.connstring, echo=self.sqlecho, pool_size=self.poolsize, pool_recycle=self.poolrecycle)
        metadata.bind = self.engine
        metadata.create_all(checkfirst=True)
        base.prepare(self.engine)

        self.db = sessionmaker()
        self.db.configure(bind=self.engine)

    def persist_samples(self, samples):
        with db_checkout(self.db) as dbsession:
            assert isinstance(dbsession, sqlalchemy.orm.session.Session)

            for sample in samples:
                assert isinstance(sample, GriffinSample)
                s = DBSample(sample.to_dict())
                dbsession.add(s)

            dbsession.commit()

    def flush(self):
        pass
