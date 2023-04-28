"""Make database session.

- Author: Kibum Park
- Contact: kibum.park@onepredict.com.
"""

from core.config import setting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    setting.servicedb_uri,
    pool_pre_ping=True,
    connect_args={"options": f"-c timezone={setting.timezone}"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
