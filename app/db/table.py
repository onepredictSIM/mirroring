"""부모 DB base 정의.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""
from typing import Any

from sqlalchemy.ext.declarative import declarative_base, declared_attr


class Base:
    """부모 DB 클래스 정의."""

    @declared_attr
    def __tablename__(cls) -> str:
        """모델의 테이블 이름을 반환합니다.

        Returns:
            str: 테이블의 이름(클래스 이름의 소문자 버전)입니다.
        """
        return cls.__name__.lower()  # type: ignore[attr-defined]

    def __getitem__(self, key: str) -> Any:
        """모델에서 속성 값을 검색합니다.

        Args:
            key (str): 속성의 이름입니다.
        반환합니다:
            Any: 속성의 값입니다.
        """
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """모델에서 속성의 값을 설정합니다.

        Args:
            key (str): 속성의 이름입니다.
            value (Any): 속성에 설정할 값입니다.


        Returns:
            None.
        """
        return setattr(self, key, value)


Base = declarative_base(cls=Base)  # type: ignore[misc]
