from dataclasses import dataclass

@dataclass
class InvestigationDecision:

    continue_investigation:bool
    reason:str

class ImvestigationDecisionService:

    def should_continue(
            self,state
    )->InvestigationDecision:

        categories={
            evidence.category
            for evidence in state.evidence_collected
        }

        if len(state.evidence_collected)<2:
            return InvestigationDecision(
                continue_investigation=True,
                reason=(
                     "Insufficient evidence "
                    "has been collected."
                )
            )

        if len(categories)<2:
            return InvestigationDecision(
                continue_investigation=True,
                reason=(
                     "Evidence lacks "
                    "independent categories."
                )
            )

        return InvestigationDecision(
            continue_investigation=False,
            reason=(
                "Sufficient evidence has"
                "been collected"
            )
        )

    