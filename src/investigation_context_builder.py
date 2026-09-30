class InvestigationContextBuilder:

    def build(self,state)->str:

        lines=[

            f"Pipeline :{state.pipeline_name}",
            f"Iteration :{state.iteration}",
            "",
            "Evidence"
        ]

        for evidence in state.evidence_collected:

            lines.append(
                f"-[{evidence.category}]"
                f"{evidence.summary}"
            )

        lines.append("")
        lines.append("Hypotheses:")

        for hypothesis in state.hypotheses:

            lines.append(
                f"-{hypothesis.description}"
            )

            lines.append(
                f"Confidence:"
                f"{hypothesis.confidence}"
            )

        return "\n".join(lines)

    def build_final_context(
            self,
            state
                  )->str:

        lines=[
            "FINAL_INVESTIGATION_CONTEXT",
            "",
            f"Pipeline:{state.pipeline_name}",
            f"Iteration:{state.iteration}",
            "",
            "Evidence:",

        ]

        for evidence in state.evidence_collected:

            lines.append(
                f"-[{evidence.category}]"
                f"{evidence.summary}"
            )

        lines.append("")
        lines.append("Hypotheses:")

        for hypothesis in state.hypotheses:

            lines.append(f"-{hypothesis.description}")

            lines.append(
                f"Confidence:"
                f"{hypothesis.confidence}"
            )

            if hypothesis.supporting_evidence:

                lines.append(
                    "Supporting evidence:"
                )

                for evidence in (
                    hypothesis.supporting_evidence
                ):
                    lines.append(
                        f"- {evidence}"
                    )

            if hypothesis.contradicting_evidence:

                     lines.append(
                "Contradicting evidence:"
            )

            for evidence in (
                hypothesis.contradicting_evidence
            ):
                lines.append(
                    f"  - {evidence}"
                )

        return "\n".join(lines)