from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker

from superagi.models.base_model import DBBaseModel
from superagi.models.db import connect_db

engine = connect_db()
Session = sessionmaker(bind=engine)


class ClusterExecution(DBBaseModel):
    """
    Represents single cluster run

    Attributes:
        id (int): The unique identifier of the cluster execution.
        status (str): The status of the cluster execution. Possible values: 'CREATED','PICKED', 'READY',
            'COMPLETED', 'WAITING', 'TERMINATED'.
        cluster_id (int): The identifier of the associated cluster.
        last_execution_time (datetime): The timestamp of the last execution time.
        num_of_calls (int): The number of calls made during the execution.
        num_of_tokens (int): The number of tokens used during the execution.
    """

    __tablename__ = 'cluster_executions'

    id = Column(Integer, primary_key=True)
    status = Column(String)  # like ('CREATED', 'PICKED', 'RUNNING', 'COMPLETED', 'WAITING', 'TERMINATED')
    cluster_id = Column(Integer)
    last_execution_time = Column(DateTime)
    num_of_calls = Column(Integer, default=0)
    num_of_tokens = Column(Integer, default=0)

    def __repr__(self):
        """
        Returns a string representation of the ClusterExecution object.

        Returns:
            str: String representation of the ClusterExecution.
        """

        return (
            f"ClusterExecution(id={self.id}, status='{self.status}', "
            f"last_execution_time='{self.last_execution_time}', "
            f"cluster_id={self.cluster_id}, num_of_calls={self.num_of_calls})"
        )

    @staticmethod
    def create_cluster_execution(cluster_id):
        """
        Creates a new cluster execution.

        Args:
            cluster_id (int): The identifier of the associated cluster.

        Returns:
            ClusterExecution: The newly created cluster execution.
        """
        session = Session()
        cluster_execution = ClusterExecution(
            status='CREATED',
            cluster_id=cluster_id,
        )
        session.add(cluster_execution)
        session.commit()
        session.close()
        return cluster_execution

    @classmethod
    def get_cluster_execution_by_id(cls, cluster_execution_id):
        """
        Gets a cluster execution by its identifier.

        Args:
            cluster_execution_id (int): The identifier of the cluster execution.

        Returns:
            ClusterExecution: The cluster execution.
        """

        session = Session()
        cluster_execution = session.query(cls).filter(cls.id == cluster_execution_id).first()
        session.close()
        return cluster_execution

    @classmethod
    def get_cluster_execution_by_status(cls, status):
        """
        Gets a cluster execution by its status.

        Args:
            status (str): The status of the cluster execution.

        Returns:
            ClusterExecution: The cluster execution.
        """

        session = Session()
        cluster_execution = session.query(cls).filter(cls.status == status).first()
        session.close()
        return cluster_execution

    @classmethod
    def get_pending_cluster_executions(cls):
        """
        Gets all pending cluster executions.

        Returns:
            list[ClusterExecution]: The list of pending cluster executions.
        """
        pending_status = ["CREATED", "PICKED", "READY"]
        session = Session()
        cluster_executions = session.query(cls).filter(cls.status.in_(pending_status)).all()
        session.close()
        return cluster_executions

    @classmethod
    def update_cluster_status(cls, cluster_execution_id, status):
        """
        Updates the status of a cluster execution.

        Args:
            cluster_execution_id (int): The identifier of the cluster execution.
            status (str): The new status of the cluster execution.
        """

        session = Session()
        cluster_execution = session.query(cls).filter(cls.id == cluster_execution_id).first()
        cluster_execution.status = status
        session.commit()
        session.close()

    @classmethod
    def update_cluster_execution(cls, cluster_execution_id, status, last_execution_time, num_of_calls, num_of_tokens):
        """
        Updates the status of a cluster execution.

        Args:
            cluster_execution_id (int): The identifier of the cluster execution.
            status (str): The new status of the cluster execution.
            last_execution_time (datetime): The timestamp of the last execution time.
            num_of_calls (int): The number of calls made during the execution.
            num_of_tokens (int): The number of tokens used during the execution.

        Returns:
            ClusterExecution: The updated cluster execution.
        """

        session = Session()
        cluster_execution = session.query(cls).filter(cls.id == cluster_execution_id).first()
        cluster_execution.status = status
        cluster_execution.last_execution_time = last_execution_time
        cluster_execution.num_of_calls = num_of_calls
        cluster_execution.num_of_tokens = num_of_tokens
        session.commit()
        session.close()
        return cluster_execution

