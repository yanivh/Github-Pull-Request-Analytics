import os

from aws_cdk import aws_glue_alpha as glue_alpha
from aws_cdk import aws_iam as iam
from constructs import Construct
from glue.core import GlueCore
from s3.infrastructure import S3


class GlueJobs(Construct):
    def __init__(
        self, scope: Construct, id: str, cdk_asset_bucket=None, glue_core: GlueCore = None, s3: S3 = None, **kwargs
    ):
        super().__init__(scope, id)
        self.env = self.node.try_get_context("env").upper()

        # Data sources
        self.cdk_asset_bucket = cdk_asset_bucket
        self.glue_core = glue_core
        self.s3 = s3
        self.root_path = os.path.split(os.getcwdb())[0].decode("utf-8")
        self.glue_jobs = {}

        self.add_job_extract_load_github_pull_requests()

    def add_job_extract_load_github_pull_requests(self):
        self.glue_jobs["extract_load_github_pull_requests"] = glue_alpha.Job(
            self,
            f"PythonShellJobExtractLoad_github_pull_requests",
            job_name=f"DE-GLJ-GITHUB-{self.env}-EXTRACT_LOAD_PULL_REQUESTS",
            description="Extract and Load github pull_requests data",
            executable=glue_alpha.JobExecutable.python_shell(
                glue_version=glue_alpha.GlueVersion.V1_0,
                python_version=glue_alpha.PythonVersion.THREE_NINE,
                script=glue_alpha.Code.from_asset(f"{self.root_path}/glue_jobs/etl/extract_load_github_repository.py"),
            ),
            role=self.glue_core.iam_role_basic,
            max_capacity=1,
            max_concurrent_runs=1,
            default_arguments={
                "--class": "GlueApp",
                "--Github_api_Secret": "Secretgithubapi",
                "--start_date": "False",
                "--owner": "grafana",
                "--repo": "grafana",
            }
        )
