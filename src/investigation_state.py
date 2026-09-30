from dataclasses import dataclass ,field

@dataclass
class ToolExecution:
   name:str
   arguments:dict

@dataclass
class EvidenceItem:

    source:str
    summary:str
    category:str

@dataclass
class Hypothesis:

    description: str

    supporting_evidence: list[str] = field(
        default_factory=list
    )

    contradicting_evidence: list[str] = field(
        default_factory=list
    )

    confidence: str = "low"

@dataclass
class InvestigationState:
    pipeline_name:str

    tools_used:list[str]=field(
        default_factory=list
    )

    tool_executions:list[ToolExecution]=field(
        default_factory=list
    )

    evidence_collected:list[str]=field(
        default_factory=list
    )

    hypotheses:list[Hypothesis]=field(
        default_factory=list
    )

    iteration:int=0

    completed:bool=False

    def record_tool(
        self,
        name: str,
        arguments: dict,
    )->None:
        self.tool_executions.append(
            ToolExecution(
                name=name,
                arguments=arguments,
            )
        )

        if name not in self.tools_used:
            self.tools_used.append(name)

    def record_evidence(
            self,
            source:str,
            summary:str,
            category:str
            
    )->None:
        self.evidence_collected.append(
            EvidenceItem(
                source=source,
                summary=summary,
                category=category
            )
        )

    def add_hypothesis(
            self,
            description:str
    )->None:

        self.hypotheses.append(
            Hypothesis(
                description=description
            )
        )

    def add_supporting_evidence(
            self,
            hypothesis:str,
            evidence:str
    )->None:

        for item in self.hypotheses:
            if item.description==hypothesis:
                item.supporting_evidence.append(
                    evidence
                )

                return

    def add_contradicting_evidence(
    self,
    hypothesis: str,
    evidence: str,
) -> None:

     for item in self.hypotheses:

        if item.description == hypothesis:

            item.contradicting_evidence.append(
                evidence
            )

            return

    def increment_iteration(
            self
    )->None:
        self.iteration+=1

    def tool_was_used(self,tool_name:str)->bool:
        return tool_name in self.tools_used

    def update_hypothesis_confidence(
    self,
    hypothesis: str,
) -> None:

     for item in self.hypotheses:

        if item.description != hypothesis:
            continue

        supporting = len(
            item.supporting_evidence
        )

        contradicting = len(
            item.contradicting_evidence
        )

        if supporting >= 3 and contradicting == 0:
            item.confidence = "high"

        elif supporting >= 2 and supporting > contradicting:
            item.confidence = "medium"

        else:
            item.confidence = "low"

        return

    def already_executed(
    self,
    name: str,
    arguments: dict,
) -> bool:

     return any(
         execution.name == name
        and execution.arguments == arguments
        for execution in self.tool_executions
    )

    def summarize(self)->str:

       lines=[
          f"Pipeline:{self.pipeline_name}",
          "",
          "Evidence"
       ]

       for evidence in self.evidence_collected:
          lines.append(
             f"-[{evidence.category}]"
             f"{evidence.summary}"
          )

       lines.append("")
       lines.append("Hypothesis:")

       for hypothesis in self.hypotheses:

          lines.append(
             f"Confidence:"
             f"{hypothesis.confidence}"
          )

       return "\n".join(lines)