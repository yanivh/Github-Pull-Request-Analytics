import os

from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3_deployment as s3deploy
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class GlueCore(Construct):
    def __init__(self, scope: Construct, id: str, cdk_asset_bucket=None, **kwargs):
        super().__init__(scope, id)
        self.env = self.node.try_get_context("env").upper()
        self.root_path = os.path.split(os.getcwdb())[0].decode("utf-8")
        self.cdk_asset_bucket = cdk_asset_bucket

        # Deploying resources
        self.add_glue_iam_role()

    def add_glue_iam_role(self):
        # Glue - IAM Role for Glue jobs with several IAM policies
        self.iam_role_basic = iam.Role(
            self,
            "IamRoleGlueJob",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="IAM role for Glue Jobs",
            role_name=f"DE-IMR-GITHUB-{self.env}-GLUE_JOB",
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AWSGlueServiceRole",
                    "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
                ),
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AmazonS3FullAccess",
                    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                ),
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "SecretsManagerReadWrite",
                    "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
                ),
            ],
        )
