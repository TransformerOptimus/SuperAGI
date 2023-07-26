from sqlalchemy import Column, Integer, Text, String

from superagi.models.base_model import DBBaseModel


class ClusterConfiguration(DBBaseModel):
    """
    Cluster related configurations like goals, etc. are stored here

    Attributes:
        id (int): The unique identifier of the cluster configuration.
        cluster_id (int): The identifier of the associated cluster.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'cluster_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Cluster Configuration object.

        Returns:
            str: String representation of the Cluster Configuration.

        """
        return f"ClusterConfiguration(id={self.id}, key={self.key}, value={self.value})"

    @classmethod
    def fetch_cluster_configuration(cls, session, cluster):
        """
        Fetches the cluster configuration for the given cluster id.

        Args:
            cluster (Cluster): The cluster object.

        Returns:
            list: List of cluster configurations.

        """
        cluster_configurations = session.query(cls).filter(cls.cluster_id == cluster.id).all()

        config = {
            "cluster_id": cluster.id,
            "name": cluster.name,
            "project_id": cluster.project_id,
            "description": cluster.description,
            "goal": [],
            "instruction": [],
            "agent_type": None,
            "constraints": None,
            "tools": [],
            "exit": None,
            "iteration_interval": None,
            "model": None,
            "permission_type": None,
            "LTM_DB": None,
        }
        for item in cluster_configurations:
            key = item.key
            value = item.value

            if key == "name":
                config["name"] = value
            elif key == "project_id":
                config["project_id"] = int(value)
            elif key == "description":
                config["description"] = value
            elif key == "goal":
                config["goal"] = eval(value)  # Using eval to parse the list of strings
            elif key == "instruction":
                config["instruction"] = eval(value)
            elif key == "agent_type":
                config["agent_type"] = value
            elif key == "constraints":
                config["constraints"] = eval(value)  # Using eval to parse the list of strings
            elif key == "tools":
                config["tools"] = eval(value)  # Using eval to parse the list of strings
            elif key == "exit":
                config["exit"] = value
            elif key == "iteration_interval":
                config["iteration_interval"] = int(value)
            elif key == "model":
                config["model"] = value
            elif key == "permission_type":
                config["permission_type"] = value
            elif key == "LTM_DB":
                config["LTM_DB"] = value

        return config

    @staticmethod
    def create_cluster_config(session, cluster_id: int, config: dict):
        """
        Creates a cluster configuration.

        Args:
            cluster_id (int): The identifier of the cluster.
            config (dict): The cluster configuration.

        Returns:
            int: The identifier of the created cluster configuration.

        """
        for key, value in config.items():
            cluster_configuration = ClusterConfiguration(cluster_id=cluster_id, key=key, value=value)
            session.add(cluster_configuration)
        session.commit()
        return cluster_id
