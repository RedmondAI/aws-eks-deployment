"""
Juno Innovations - EKS Infrastructure for Orion
"""

# local
from src import JunoAccount, JunoRegion, Cluster, set_repositories, set_profile, set_session

# set the root account
JunoAccount.set_root_account("r3d")

# set AWS session and profiles
set_profile("cosmos")  # this should be an account that can assume other accounts and have specific permissions to do so
set_session("cosmos")  # this is a trackable session name

# bootstrap
Cluster.set_bootstrap_repository(
    repository="https://github.com/RedmondAI/aws-eks-deployment.git",
    path="bootstrap/",
)

# ECR repositories
set_repositories(
    [
        # juno images
        "hubble",
        "kuiper",
        "titan",
        "polaris-workstation",
        "mars",
        "luna",
        "webb",
        "pluto",
        "terra",
        "mercury",
        "genesis",
    ]
)


# account and regional deployments
with JunoAccount("sandbox"):
    with JunoRegion("us-east-2", ecr_master=True):
        with Cluster("192.168.0.0") as cluster:
            cluster.add_node_group(
                name="service",
                instances=["c6a.xlarge", "t3.xlarge"],
                capacity_type=cluster.CapacityType.SPOT,
                minimum=1,
                size=1,
                maximum=5,
            )
            cluster.add_node_group(
                name="workstation",
                instances=["g4dn.2xlarge"],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=0,
                size=0,
                maximum=3,
                resource_name="gpu-workstation",
                labels={"nvidia/gpu": "true"},
            )
            cluster.add_node_group(
                name="r3dc",
                instances=["t3.xlarge"],
                capacity_type=cluster.CapacityType.SPOT,
                minimum=0,
                size=0,
                maximum=5,
                resource_name="r3d-cpu",
                labels={"r3d/mode": "cpu"}
            )
            cluster.add_node_group(
                name="r3dg",
                instances=["g6e.2xlarge"],
                capacity_type=cluster.CapacityType.SPOT,
                minimum=0,
                size=0,
                maximum=5,
                resource_name="r3d-gpu",
                labels={"r3d/mode": "gpu"}
            )