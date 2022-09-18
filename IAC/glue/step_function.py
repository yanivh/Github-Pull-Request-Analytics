import aws_cdk as cdk
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from aws_cdk import aws_sns as sns
from constructs import Construct
from aws_cdk import aws_glue_alpha as glue_alpha
from glue.jobs import GlueJobs


class GlueStepFunctions(Construct):
    def __init__(self, scope: Construct, id: str, cdk_asset_bucket=None, glue_jobs: GlueJobs = None, **kwargs):
        super().__init__(scope, id)
        self.env = self.node.try_get_context("env").upper()

        self.glue_jobs = glue_jobs
        self.cdk_asset_bucket = cdk_asset_bucket

        # Create IAM resources
        self.iam_role_sfn = None
        self.iam_role_events_bridge = None
        self.add_iamrole_step_functions()

        # Deploy step function
        pullrequest_loader = self.add_github_pullrequest_loader()

        success_sns = self.publish_success_task()

        # # Create State Machine
        sfn_state_machine = sfn.StateMachine(
            self,
             "StateMachineGithubPrLoader",
             state_machine_name=f"DE-SFN-GITHUB-{self.env}-PULL_REQUEST_LOADER",
             definition= pullrequest_loader.next(success_sns),
             # definition=success_sns,
             role=self.iam_role_sfn,
             timeout=cdk.Duration.minutes(60),
         )

         # Create CRON which triggers this State Machine
        rule = events.Rule(
             self,
             "EventBridgeRuleGithubEpLoader",
             rule_name=f"DE-EBR-GITHUB-{self.env}-PUULREQUEST_LOADER",
             schedule=events.Schedule.cron(minute="1", hour="7", month="*", year="*", day="*"),
             targets=[targets.SfnStateMachine(sfn_state_machine, role=self.iam_role_events_bridge)],
         )

    def add_iamrole_step_functions(self):
        # IAM Role - Step functions
        self.iam_role_sfn = iam.Role(
            self,
            "IamRoleStepFunctions",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            description="IAM role for Step Function",
            role_name=f"DE-IMR-GITHUB-{self.env}-STEP_FUNCTIONS",
        )

        # IAM Role - EventBridge
        self.iam_role_events_bridge = iam.Role(
            self,
            "IamRoleEventBridge",
            assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
            description="IAM role for EventBridge",
            role_name=f"DE-IMR-GITHUB-{self.env}-EVENT_BRIDGE",
        )

        self.iam_role_events_bridge.attach_inline_policy(
            iam.Policy(
                self,
                "EventBridge",
                statements=[iam.PolicyStatement(actions=["states:StartExecution"], resources=["*"])],
            )
        )

        # Deploy step function
        # self.add_github_pullrequest_loader()

    def publish_success_task(self):
        _sns = sfn_tasks.SnsPublish(self, "Success",
                                      topic=sns.Topic.from_topic_arn(self,
                                                                     "Publishsuccess",
                                                                     "arn:aws:sns:{}:{}:pullRequest-pipeline-complete".format(
                                                                         "aws_region",
                                                                         "aws_account_id",
                                                                         )),
                                      message=sfn.TaskInput.from_json_path_at(
                                          "States.Format('Pipeline run success)"
                                      )
                                      )
        return _sns

    def add_github_pullrequest_loader(self):
        """This method will create the state machine for CompassGroup_ETL"""

        # Step 1. - Run extract load job which load the data from github api into S3
        load_ = sfn_tasks.GlueStartJobRun(
            self,
            id = 'Run_GlueJob-extract_load_github_repository.py',
            glue_job_name=self.glue_jobs.glue_jobs["extract_load_github_pull_requests"].job_name,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        return load_
