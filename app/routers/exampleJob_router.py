
from fastapi import APIRouter
from models.executed_jobs import ExecutedJob, create_log
from datetime import datetime
from logger_module.logger_config import LoggerSingleton
from app.utils.config import settings
from app.utils.utils_job import control_job_id,log_job_completion_status

from common.constants.enum import StatusEnum
logger = LoggerSingleton(settings.LOG_LEVEL).logger
router = APIRouter()

@router.post("/api/print")
def api_print_message(id_ex_jobs: int):
    
    try:
        """"verify if the transmitted ID corresponds to an existing CREATED line"""
        output = control_job_id(id_ex_jobs)
        #treating the job
        success = True 
        
        new_execution = log_job_completion_status(success,output["ex_job.job_id"])

        return {
            "status": new_execution["final_status"].value,
            "started_execution_id": output["started_execution_id"],
            "final_execution_id": new_execution["id"]
        }

    except Exception as e:
        create_log(output["ex_job.job_id"],  StatusEnum.ERROR)
        logger.error(f"Erreur lors de l'exécution du traitement métier: {e}") 
       