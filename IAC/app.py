#!/usr/bin/env python3
# Project structure based on https://github.com/aws-samples/aws-cdk-project-structure-python

import aws_cdk as cdk
from aws_cdk import CfnParameter, DefaultStackSynthesizer, Stack, aws_s3
from constructs import Construct
from glue.core import GlueCore
from glue.jobs import GlueJobs
from glue.step_function import GlueStepFunctions
from s3.infrastructure import S3


class GitHubAnalytics(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        cdk_asset_bucket = aws_s3.Bucket.from_bucket_name(
            self,
            "CdkAssetBucket",
            bucket_name=self.synthesizer.deploy_role_arn.rsplit("/")[-1].replace("deploy-role", "assets"),
        )

        # cdk.Tags.of(self).add("aws.cloudformation.stack-id", self.stack_id)
        cdk.Tags.of(self).add("aws.cloudformation.stack-name", self.stack_name)

        s3 = S3(self, "S3")
        glue_core = GlueCore(self, "Glue", cdk_asset_bucket=cdk_asset_bucket)
        glue_jobs = GlueJobs(self, "GlueJobs", cdk_asset_bucket=cdk_asset_bucket, glue_core=glue_core, s3=s3)
        glue_workflow_sfn = GlueStepFunctions(
            self, "GlueWorkflowSFN", cdk_asset_bucket=cdk_asset_bucket, glue_jobs=glue_jobs
        )


def get_env(app: cdk.App):
    aws_env = {
        "snd": cdk.Environment(account="177806169472", region="eu-west-1"),
        "dev": cdk.Environment(account="177806169472", region="eu-central-1"),
        "prod": cdk.Environment(account="177806169472", region="eu-central-1"),
    }

    env = app.node.try_get_context("env")
    if env not in ["snd", "dev", "prod"]:
        raise ValueError(f"Allowed environments: ['snd', 'dev', 'prod'] not '{env}'")
    return aws_env[env]


app = cdk.App()
GitHubAnalytics(app, "GitHubAnalytics", env=get_env(app))
app.synth()
