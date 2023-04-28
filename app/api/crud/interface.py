from typing import Any, Callable, Dict, Generic, List, TypeVar, Union

from sqlalchemy import and_
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import sessionmaker

T = TypeVar("T")


class AnalysisSQL:
    def __init__(
        self, columns: List[str], SessionLocal: sessionmaker, orm_class: Generic[T]
    ):
        self.columns = columns
        self.local_session = SessionLocal
        self.orm_cls = orm_class

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def check_order_by_condition(self, **kwargs) -> Union[Callable, None]:
        """order by 조건 있는지를 체크하고, 있을 경우  해당 옵션으로 order by 함.
        만약 옵션을 이상하게 줬으면 디폴트 옵션은 시간순서대로 order by 하게 설정함.
        """
        if kwargs.get("order_by_condition") is None:
            return None
        else:
            return getattr(
                getattr(
                    self.orm_cls,
                    kwargs.get("order_by_condition").get("column", "acq_time"),
                ),
                kwargs.get("order_by_condition").get("option", "asc"),
            )()

    def check_between_condition(self, **kwargs):
        """order by 조건 있는지를 체크하고, 있을 경우  해당 옵션으로 order by 함.
        만약 옵션을 이상하게 줬으면 디폴트 옵션은 시간순서대로 order by 하게 설정함.
        """
        if kwargs.get("between_condition") is None:
            return []
        return [
            getattr(self.orm_cls, kwargs.get("between_condition").get("column"))
            > kwargs.get("between_condition").get("from"),
            getattr(self.orm_cls, kwargs.get("between_condition").get("column"))
            < kwargs.get("between_condition").get("end"),
        ]

    def load_query_result(self, **kwargs) -> List[Dict[str, Any]]:
        with self.local_session() as session:
            query_results = (
                session.query(
                    *[getattr(self.orm_cls, column) for column in self.columns]
                )
                .filter(and_(*self.check_between_condition(**kwargs)))
                .filter_by(**(kwargs.get("equal_condition", {})))
                .order_by(self.check_order_by_condition(**kwargs))
                .limit(kwargs.get("limit_condition", None))
                .all()
            )
        return list(map(lambda x: x._asdict(), query_results))
