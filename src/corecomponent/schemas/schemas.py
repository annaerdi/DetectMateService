from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Schema:
    __version__: str = "1.0.0"


@dataclass
class LogSchema(Schema):
    logID: int = 0
    log: str = ""
    logSource: str = "example-source"
    hostname: str = "example.com"


@dataclass
class ParserSchema(Schema):
    parserType: str = ""
    EventID: int = 0
    template: str = ""
    variables: List[Any] = field(default_factory=list)
    parserID: int = 0
    logID: int = 0
    log: str = ""
    logFormatVariables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectorSchema:
    detectorID: int = 0
    detectorType: str = ""
    alertID: int = 0
    detectionTimestamp: int = 0
    logID: List[str] = field(default_factory=list)
    predictionLabel: bool = False
    score: float = 0.2
    extractedTimestamps: List[int] = field(default_factory=list)
