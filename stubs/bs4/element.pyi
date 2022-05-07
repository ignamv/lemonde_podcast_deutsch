from typing import Dict, List

class PageElement:
    pass

class Tag(PageElement):
    attrs: Dict[str,str]
    text: str
    def find(self, name: str, attrs: Dict[str,str] = ..., class_: str = ..., id: str = ..., **kwargs: str) -> Tag: ...
    def find_all(self, name: str, attrs: Dict[str,str] = ..., class_: str = ..., id: str = ..., **kwargs: str) -> List[Tag]: ...
