from aws_cdk import aws_s3 as s3
from constructs import Construct


class S3(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id)
        self.env = self.node.try_get_context("env").upper()

        # S3 bucket for data
        self.bucket_data = s3.Bucket(
            self,
            "DataBucket",
            bucket_name=f"DE-Mbition-Analytics-{self.env}-DATALAKE".lower(),
            encryption=s3.BucketEncryption.S3_MANAGED,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
