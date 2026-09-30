from dataclasses import dataclass,field

@dataclass
class ToolCall:
    id:str
    name:str
    arguments:dict

@dataclass
class LLMResponse:
    content:str|None
    tool_calls:list[ToolCall]
    assistant_message:dict|None=None


@dataclass
class InvestigationResult:

    pipeline_name:str
    summary:str
    severity:str
    confidence:str
    evidence:list[str]=field(
        default_factory=list
    )
    hypotheses:list[str]=field(
        default_factory=list
    )
    recommendations: list[str] = field(
        default_factory=list
    )

    uncertainty: list[str] = field(
        default_factory=list
    )