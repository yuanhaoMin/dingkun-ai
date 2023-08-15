from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://username:password@localhost/dbname"
SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://root:root@localhost/uwb_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class UwbPatrolLog(Base):
    __tablename__ = 'uwb_patrol_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_id = Column(Integer)
    patrol_code = Column(String(255))
    patrol_name = Column(String(255))
    person_code = Column(Integer)
    area_code = Column(Integer)
    into_time = Column(DateTime)
    out_time = Column(DateTime)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
