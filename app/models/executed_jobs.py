import enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from common.db.database import Base
from common.db.database import SessionLocal
from datetime import datetime
from common.exceptions.exceptions import ErrorCode, TechnicalException
from common.utils.logger_config import LoggerSingleton
from common.constants.enum import StatusEnum
from sqlalchemy.exc import SQLAlchemyError


logger = LoggerSingleton("INFO").logger


class ExecutedJob(Base):
    __tablename__ = "executed_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True , comment="Execution identifier")
    status = Column(Enum(StatusEnum, native_enum=False), nullable=False,comment="Execution status")
    execution_date = Column(DateTime, default=func.now(), comment="Execution date")
    job_id = Column(Integer, ForeignKey("jobs.id"), comment="Job identifier")

    job = relationship("Job")


def create_log(job_id, status):
    try:
        db = SessionLocal()
        execution = ExecutedJob(
            job_id=job_id,
            status=StatusEnum(status),
            execution_date=datetime.now()
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution.id
    except Exception as e:
        db.rollback()
        print(f"Erreur création log: {e}")
        return None
    finally:
        db.close()
        
def update_log(job_execution_id: int, status):
    """
    Update an existing ExecutedJob.

    Args:
        job_execution_id: ID of the row in executed_jobs
        status: StatusEnum value

    Returns:
        The updated ExecutedJob, or None if not found / error occurred.
    """
    try:
        db = SessionLocal()
        ej = db.get(ExecutedJob, job_execution_id)
        if not ej:
            logger.warning(f"ExecutedJob {job_execution_id} not found.")
            return None

        ej.status = status if isinstance(status, StatusEnum) else StatusEnum(status)

        ej.execution_date = datetime.now()

        db.commit()
        db.refresh(ej)
        return ej
    except Exception as e:
        db.rollback()
        logger.error(f"An error occurred while updating log {job_execution_id}: {e}")
        raise TechnicalException(
            f"Error updating log {str(e)}",
            error_code=ErrorCode.DATABASE_ERROR
        ) from e
    finally:
        db.close()

def get_job_by_id_with_created_status(job_id):
    """
    Retreive an object with a specific ID with status CREATED.
    
    Args:
        session: Database session
        job_id: Object ID to retrieve
        
    Returns:
        Found Job or None if no corresponding job is found
    """
    try:
        session = SessionLocal()
        result = session.query(ExecutedJob).filter(
            ExecutedJob.id == job_id,
            ExecutedJob.status == StatusEnum.CREATED
        ).first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving job by ID: {e}")
        raise TechnicalException(
            f"Error retrieving job by ID {str(e)}",
            error_code=ErrorCode.DATABASE_ERROR
        ) from e
    finally:
        session.close()