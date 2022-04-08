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
