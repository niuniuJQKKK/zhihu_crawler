from typing import Any, Callable, Dict, Iterable, Tuple, List, Union, Optional, Set, Iterator
from requests_html import Element
from requests import Response

URL = str
Options = Dict[str, Any]
RawPage = Element
RawPost = Element
Page = Iterable[RawPost]
Credentials = Tuple[str, str]
RequestFunction = Callable[[URL], Response]
ArticleType = Dict[str, Any]
QuestionType = Dict[str, Any]
UserType = Dict[str, Any]
Keyword = Dict[str, List]
AnswerType = Dict[str, Any]
PinType = Dict[str, Any]
VideoType = Dict[str, Any]
ColumnType = Dict[str, Any]
CommentType = Dict[str, Any]
PartialType = Optional[Dict[str, Any]]
