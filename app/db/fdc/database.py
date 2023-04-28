"""Make database session.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""

from core.config import setting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(setting.fdcdb_uri, pool_pre_ping=True)
FDCSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
