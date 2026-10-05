"""
Juno Innovations - EKS Infrastructure for Orion
"""
# local
from src import JunoAccount, JunoRegion, Cluster, set_repositories, set_profile, set_session

# set the root account
JunoAccount.set_root_account("cosmos")                 # this is the root account that will be used to manage the other accounts

# set AWS session and profiles
set_profile("cosmos")                                      # this should be an account that can assume other accounts and have specific permissions to do so
set_session("cosmos")                                  # this is a trackable session name

# bootstrap
Cluster.set_bootstrap_repository(
    repository="https://github.com/RedmondAI/eks-bootstap.git",     # this is the repository that will be used to bootstrap the cluster
    path="bootstrap/",                                                  # this is the path within the repository that contains the bootstrap helm chart
    ref="main",                                                         # this is the branch or tag that will be used to bootstrap the cluster
    domain="fngs.io"                                                # this is the domain that will be used to create the cluster
)

# ECR repositories
# These are the repositories that will be used to store the images for the
# cluster. If you are planning on bringing your own images, you can disable
# this block.
set_repositories([
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
    "genesis"
])


# account and regional deployments
with JunoAccount("sandbox"):                    # this is the account that will be used to deploy the clusters
    with JunoRegion("us-east-2", ecr_master=True):        # this is the region that the clusters will be deployed to
        # pass
        # example private cluster
        with Cluster(private=True) as cluster:
            # standard service node setup
            cluster.add_node_group(
                name="service",
                instances=["c6a.xlarge", "t3.xlarge"],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=1,
                size=5,     # initial only; cluster-autoscaler owns desired size afterwards
                maximum=10, # raised from 5 after 2026-10-05 service-node memory exhaustion
                labels={
                    "juno-innovations.com/service": "true"
                }
            )
        
            # example render node setup flagged for headless workloads and is GPU enabled
            cluster.add_node_group(
                gpu=True,
                name="render",
                instances=[
                    "g5.xlarge"
                ],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=0,
                size=0,
                maximum=150,
                labels={
                    "juno-innovations.com/headless": "true",
                    "nvidia/gpu": "true",
                    "render": "true"
                },
                taints=["juno-innovations.com/headless"]
            )
        
            # example render node setup flagged for workstation workloads and is GPU enabled
            cluster.add_node_group(
                gpu=True,
                name="workstation",
                instances=[
                    "g5.2xlarge"
                ],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=0,
                size=0,
                maximum=40,
                labels={
                    "juno-innovations.com/workstation": "true",
                    "nvidia/gpu": "true",
                    "workstation": "true"
                },
                taints=["juno-innovations.com/workstation"]
            )

            cluster.add_node_group(
                gpu=True,
                name="heavy",
                instances=[
                    "g5.8xlarge"
                ],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=0,
                size=0,
                maximum=40,
                labels={
                    "nvidia/gpu": "true",
                    "r3d/heavy": "true"
                },
                taints=["r3d/heavy"]
            )

            # # example render node setup flagged for workstation workloads and is GPU enabled
            # cluster.add_node_group(
            #     gpu=True,
            #     name="workstation",
            #     instances=[
            #         "g5.2xlarge"
            #         # "c7a.8xlarge",
            #         # "m6a.4xlarge",
            #         # "m5a.4xlarge",
            #         # "m7a.4xlarge",
            #         # "r5.2xlarge",
            #         # "r6a.2xlarge",
            #         # "r7i.2xlarge"
            #     ],
            #     capacity_type=cluster.CapacityType.ON_DEMAND,
            #     minimum=0,
            #     size=0,
            #     maximum=40,
            #     labels={
            #         "juno-innovations.com/workstation": "true",
            #         "nvidia/gpu": "true",
            #         "workstation": "true"
            #     },
            #     taints=["juno-innovations.com/workstation"]
            # )

            # example render node setup flagged for workstation workloads and is GPU enabled
            cluster.add_node_group(
                gpu=False,
                name="workstation-cpu",
                instances=[
                    "c7a.8xlarge",
                    "m6a.4xlarge",
                    "m5a.4xlarge",
                    "m7a.4xlarge",
                    "r5.2xlarge",
                    "r6a.2xlarge",
                    "r7i.2xlarge"
                ],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=0,
                size=0,
                maximum=40,
                labels={
                    "juno-innovations.com/workstation": "true",
                    "nvidia/gpu": "false",
                    "workstation": "true"
                },
                taints=["juno-innovations.com/workstation"]
            )
        

            # example render node setup flagged for workstation workloads and is GPU enabled
            cluster.add_node_group(
                gpu=True,
                name="dev",
                instances=[
                    "g6e.xlarge",
                    "g6e.2xlarge",
                    "g6e.4xlarge",
                    "g6e.8xlarge"
                    # "c7a.8xlarge",
                    # "m6a.4xlarge",
                    # "m5a.4xlarge",
                    # "m7a.4xlarge",
                    # "r5.2xlarge",
                    # "r6a.2xlarge",
                    # "r7i.2xlarge"
                ],
                capacity_type=cluster.CapacityType.ON_DEMAND,
                minimum=0,
                size=0,
                maximum=20,
                labels={
                    "nvidia/gpu": "true",
                    "r3d/dev": "true"
                },
                taints=["r3d/dev"]
            )
            # # example render node setup flagged for workstation workloads and is GPU enabled
            # cluster.add_node_group(
            #     gpu=True,
            #     name="workstation",
            #     instances=[
            #         "g5.2xlarge"
            #     ],
            #     capacity_type=cluster.CapacityType.ON_DEMAND,
            #     minimum=0,
            #     size=0,
            #     maximum=40,
            #     labels={
            #         "juno-innovations.com/workstation": "true",
            #         "nvidia/gpu": "true",
            #         "workstation": "true"
            #     },
            #     taints=["juno-innovations.com/workstation"]
            # )

            cluster.update_cluster_roles()
        # # example public cluster
        # with Cluster() as cluster:
        #     # standard service node setup
        #     cluster.add_node_group(
        #         name="service",
        #         instances=["c6a.xlarge", "t3.xlarge"],
        #         capacity_type=cluster.CapacityType.SPOT,
        #         minimum=1,
        #         size=1,
        #         maximum=5,
        #         labels={
        #             "juno-innovations.com/service": "true"
        #         }
        #     )
