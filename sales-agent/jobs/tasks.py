"""
Background tasks for agent execution
"""

from jobs.celery_app import celery_app
from models.database import SessionLocal
from agent.executor import AgentExecutor


@celery_app.task(name='execute_agent', bind=True, max_retries=3)
def execute_agent_task(self, execution_id: int):
    """
    Execute sales agent in background

    Args:
        execution_id: ID of the execution to run
    """
    db = SessionLocal()

    try:
        print(f"Starting execution {execution_id}")

        # Create executor and run
        executor = AgentExecutor(db)
        result = executor.execute(execution_id)

        print(f"Execution {execution_id} completed: {result}")

        return result

    except Exception as e:
        print(f"Execution {execution_id} failed: {str(e)}")

        # Retry on failure
        try:
            self.retry(exc=e, countdown=60)  # Retry after 60 seconds
        except self.MaxRetriesExceededError:
            print(f"Max retries exceeded for execution {execution_id}")
            return {"error": str(e), "max_retries_exceeded": True}

    finally:
        db.close()
