"""ExceptionClass를 담은 파일.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""


class ArgumentError(Exception):
    """잘못된 인자가 들어있을 때 Exception handling 하는 클래스."""

    def __init__(self) -> None:
        """에러 문구 작성."""
        super().__init__("함수 인자가 잘못된 값이 입력되었습니다.")


class EmptyQueryResultError(Exception):
    """쿼리 결과가 없을 때 Exception handling 하는 클래스."""

    def __init__(self) -> None:
        """에러 문구 작성."""
        super().__init__("쿼리 결과가 없습니다.")


class EmptyKeyListError(Exception):
    """딕셔너리 키가 없을 때 Exception handling 하는 클래스."""

    def __init__(self) -> None:
        """에러 문구 작성."""
        super().__init__("키 리스트가 비어있습니다.")
