from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, func
from app.database import Base

class WorkflowExecutionLog(Base):
    __tablename__ = "workflow_execution_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_name = Column(String(100), nullable=False, index=True)
    execution_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    duration_seconds = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    error_message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)

class DashboardValidationLog(Base):
    __tablename__ = "dashboard_validation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    validation_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    consistency_percentage = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # PASS, FAIL
    comparisons = Column(JSON, nullable=False)
    mismatches = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

class PerformanceTestResult(Base):
    __tablename__ = "performance_test_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    endpoint = Column(String(150), nullable=False, index=True)
    avg_response_time_ms = Column(Float, nullable=False)
    min_response_time_ms = Column(Float, nullable=False)
    max_response_time_ms = Column(Float, nullable=False)
    p95_response_time_ms = Column(Float, nullable=False)
    requests_per_sec = Column(Float, nullable=False)
    failure_rate_pct = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # PASS, FAIL
    target_met = Column(Boolean, nullable=False, default=True)
