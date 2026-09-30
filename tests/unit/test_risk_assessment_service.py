from incident_investigator.services.risk_assessment_service import(
    RiskAssessmentService,
)

def test_calculate_risk_level():
    service=RiskAssessmentService()

    assert service.calculate_risk_level(10)=="low"
    assert service.calculate_risk_level(30)=="medium"
    assert service.calculate_risk_level(60) == "high"
    assert service.calculate_risk_level(80) == "critical"

def test_failure_streak_adds_risk():
    service=RiskAssessmentService()

    result=service.calculate_risk(
        failure_streak=3,
        duration_anomaly=False,
        rows_read_anomaly=False,
        rows_written_anomaly=False,
        repeated_errors=0,
        dependency_issue=False,
        deployment_correlation_score=None
    )

    assert result.score==20
    assert result.risk_level=="low"

def test_strong_deployment_correlation_adds_risk():

    service=RiskAssessmentService()

    result=service.calculate_risk(
        failure_streak=0,
        duration_anomaly=False,
        rows_read_anomaly=False,
        rows_written_anomaly=False,
        repeated_errors=0,
        dependency_issue=False,
        deployment_correlation_score=6,
    )

    assert result.score==15
    assert result.risk_level=="low"

def test_multiple_risk_factors():
    service = RiskAssessmentService()

    result = service.calculate_risk(
        failure_streak=3,
        duration_anomaly=True,
        rows_read_anomaly=True,
        rows_written_anomaly=True,
        repeated_errors=2,
        dependency_issue=True,
        deployment_correlation_score=6,
    )

    assert result.score == 100
    assert result.risk_level == "critical"

def test_no_risk_factors():
    service=RiskAssessmentService()

    result=service.calculate_risk(
        failure_streak=0,
        duration_anomaly=False,
        rows_read_anomaly=False,
        rows_written_anomaly=False,
        repeated_errors=0,
        dependency_issue=False,
        deployment_correlation_score=None
    )

    assert result.score==0
    assert result.risk_level=="low"
    assert result.factors==[]

def test_deployment_risk_points():
    service = RiskAssessmentService()

    assert service.deployment_risk_points(0) == 0
    assert service.deployment_risk_points(2) == 5
    assert service.deployment_risk_points(4) == 10
    assert service.deployment_risk_points(6) == 15