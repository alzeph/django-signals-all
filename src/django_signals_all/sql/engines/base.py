from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ParsedStatement:
    operation: str
    table: str | None


class ParseEngine(Protocol):
    def parse(self, sql: str, vendor: str) -> ParsedStatement | None: ...
