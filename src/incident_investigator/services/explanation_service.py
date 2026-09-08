from incident_investigator.models.evidence_chain import EvidenceChain


class ExplanationService:
    def build_error_chain(self, error_pattern) -> EvidenceChain | None:

        if error_pattern.occurrences < 2:
            return None

        if error_pattern.category == "connection_timeout":

            return EvidenceChain(
                observation=("Repeated connection timeout errors" "were detected"),
                evidence=[
                    (
                        f"{error_pattern.occurrences}"
                        "connection timeout events were detected."
                    ),
                ],
                correlation=(
                    "Repeated timeout events were observed"
                    "during the failing pipeline run."
                ),
                hypothesis=(
                    "A downstream system may have been "
                    "unavailable or responding slowly."
                ),
                confidence=("high" if error_pattern.occurrences >= 3 else "medium"),
                recommendation=[
                    "check downstream system availablity"
                    "check network connectivity"
                    "Review connection timeout settings"
                ],
            )

        if error_pattern.category == "authentication_failure":

            return EvidenceChain(
                observation=("Authentication-related failures " "were detected."),
                evidence=[
                    (
                        f"{error_pattern.occurrences} "
                        "authentication failures were detected."
                    )
                ],
                correlation=(
                    "Authentication failures occurred " "during the failed run."
                ),
                hypothesis=(
                    "Pipeline credentials may be invalid, "
                    "expired, or incorrectly configured."
                ),
                confidence=("high" if error_pattern.occurrences >= 3 else "medium"),
                recommendations=[
                    "Verify credentials.",
                    "Check whether secrets were recently rotated.",
                    "Check authentication configuration.",
                ],
            )

        if error_pattern.category == "schema_mismatch":

            return EvidenceChain(
                observation=("Schema-related errors were detected."),
                evidence=[
                    (
                        f"{error_pattern.occurrences} "
                        "schema-related errors were detected."
                    )
                ],
                correlation=(
                    "Schema errors occurred during " "the failing pipeline run."
                ),
                hypothesis=("The source or destination schema " "may have changed."),
                confidence=("high" if error_pattern.occurrences >= 3 else "medium"),
                recommendations=[
                    "Compare current schema with expected schema.",
                    "Check recent source-system schema changes.",
                    "Check pipeline transformation mappings.",
                ],
            )

    def build_error_chains(self, error_patterns) -> list[EvidenceChain]:

        chains = []

        for error_pattern in error_patterns:
            chain = self.build_error_chain(error_pattern)

            if chain is not None:
                chains.append(chain)

        return chains

    def build_dependency_chain(self, dependency) -> EvidenceChain:

        return EvidenceChain(
            observation=(
                f"Logs referenced dependency"
                f"'{dependency.dependency_name}"
                "shortly before failure"
            ),
            evidence=[
                (
                    f"{dependency.matched_logs} logs matched"
                    f"the dependency"
                    f"'{dependency.dependency_name}'"
                ),
                *dependency.evidence,
            ],
            correlation=(
                f"The dependency"
                f"'{dependency.dependency_name}'"
                "Was referenced close to the pipeline failure."
            ),
            hypothesis=(
                f"The dependency"
                f"'{dependency.dependency_name}'"
                "may have contributed to the incident"
            ),
            confidence=dependency.confidence,
            recommendation=[
                (
                    f"Check the health and availablity of "
                    f"'{dependency.dependency_name}'"
                )
            ],
        )

    def build_duration_chain(self, duration_anomaly) -> EvidenceChain | None:

        if not duration_anomaly.detected:
            return None

        ratio = duration_anomaly.duration_ratio

        return EvidenceChain(
            observation=(
                "the latest pipeline run took" "singnificantly longer than normal"
            ),
            evidence=[
                f"The latest duration was" f"{ratio:.1f}x the historical average."
            ],
            correlation=(
                "the abnormal execution duration occured" "during the failing run."
            ),
            hypothesis=(
                "The pipeline may have experienced "
                "resource contention, slow dependencies, "
                "or increased processing latency."
            ),
            confidence="medium",
            recommendations=[
                "check slow external dependencies",
                "check database query performance" "Review resource utilization",
            ],
        )

    def build_row_count_chain(self, row_count_anomaly) -> EvidenceChain | None:

        evidence = []

        if row_count_anomaly.rows_read_anomaly:

            evidence.append(
                ("Input row was significantly" "below its historical average")
            )

        if row_count_anomaly.rows_written_anomaly:

            evidence.append(
                ("output row volume was significantly" "below its historical average")
            )

        if not evidence:
            return None

        return EvidenceChain(
            obeservation=("Abnormal data volume was detected"),
            evidence=evidence,
            correlation=(
                "The abnormal row counts were observed"
                "during the failing pipeline run."
            ),
            hypothesis=(
                "The pipeline may have received incomplete"
                "input data or failed during processing"
            ),
            confidence="medium",
            recommendation=[
                "Validate source data availability.",
                "Check extraction filters.",
                "Review transformation failures.",
            ],
        )

    def build_evidence_chains(
            self,
            error_patterns,
            dependency_analysis,
            duration_anomaly,
            row_count_anomaly
    )->list[EvidenceChain]:

        chains=[]

        chains.extend(
            self.build_error_chain(
                error_patterns
            )
        )

        for dependency in dependency_analysis:
            chains.append(
                self.build_dependency_chain(
                    dependency
                )
            )

        duration_chain=(
            self.build_duration_chain(
                duration_anomaly
            )
        )

        if duration_chain is not None:
            chains.append(duration_chain)

        row_chain=(
            self.build_row_count_chain(
                row_count_anomaly
            )
        )

        if row_chain is not None:
            chains.append(row_chain)

        return chains

    def build_deployment_chains(
            self,
            deployments,
            failure_time
    ):
        chains=[]

        for deployment in deployments:
            minutes_before_failure=(
                failure_time-deployment.deployed_at
            ).total_seconds()/60

            chains.append(
                EvidenceChain(
                    observation=(
                        f"A deployment of"
                        f"'{deployment.service_name}'"
                        f"occured before the pipeline failure."
                    ),

                    evidence=[
                        (
                            f"Version {deployment.version}"
                            f"was deployed"
                            f"{minutes_before_failure:.1f}"
                            "minutes before failure"
                        ),
                        (
                            f"Deployment environment:"
                            f"{deployment.environment}."
                        ),
                        (
                            f"Commit: "
                            f"{deployment.commit_sha or 'unknown'}"
                        )
                    ],

                    correlation=(
                         "The deployment occurred within "
                    "the investigation window before "
                    "the pipeline failure."
                    ),

                    hypothesis=(
                        f"The deployment of"
                        f"'{deployment.service_name}'"
                        "may have introduced a change"
                        "related to the incident."
                    ),

                     confidence=(
                    "high"
                    if minutes_before_failure <= 30
                    else "medium"
                ),

                recommendations=[
                    (
                        f"Review changes introduced in "
                        f"version {deployment.version}."
                    ),
                    (
                        f"Inspect commit "
                        f"{deployment.commit_sha or 'associated commit'}."
                    ),
                ],

                )
            )