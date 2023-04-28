"""Make database session.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""

from core.config import setting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    setting.metadatadb_uri,
    pool_pre_ping=True,
    connect_args={"options": f"-c timezone={setting.timezone}"},
)
MetadataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
