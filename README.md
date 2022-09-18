# Github Analytics

GitHub Anlytics, pull new data about the Grafana repository into a database.

- **GitHub API:** using GitHub's REST API v3.
with knowing that every pull request is an issue, but not every issue is a pull request. 
For this reason, **"Issues"** endpoints may return both issues and pull requests in the response. 
You can identify pull requests by the **pull_request** key.
using TokenAPI is store in **AWs secret manger** called **Secretgithubapi**

- **infrastructure as a code:** Infrastructure as Code (IaC) is the managing and provisioning of infrastructure through code instead of through manual processes. With IaC, configuration files are created that contain your infrastructure specifications, which makes it easier to edit and distribute configurations  
<pre>
 Github-Analytics -IAC
 IAC/S3 -  datalake storage
 IAC/glue/jobs - extract load , execute a python script
 IAC/glue/core - create IAM role's
 IAC/step_function - orcastrate the data ingestion.
</pre>

- **Extract Load:** Amazon **Glue** has a serverless architecture that been used in this project for **Extract** and **load** and **catalog** data. in addtion give the option to paramertize the Job , include new owner , new repo , and specific date.
<pre>
 start_date = date(2022, 9, 11)
 git_owner = 'grafana'
 git_repo = 'grafana'

 args = {
         "GithubApiSecret": "Secretgithubapi",
         "start_date": f"{str(start_date)}",
         "GitOwner": f"{git_owner}",
         "GitRepo": f"{git_repo}",
        }
</pre>


- **Query engine.:** Amazon  **Athena** has a serverless architecture that automatically scales to tens of thousands of users without the need to setup, configure, or manage your own servers.Athena integrated with **AWS Glue Data Catalog**, allowing you to create a unified metadata repository across various services, crawl data sources to discover schemas and populate your Catalog with new and modified table 
and **partition** definitions, and maintain **schema versioning**

<pre>
CREATE EXTERNAL TABLE `pull_requests`(
  `id` bigint,
  `number` bigint,
  `title` string,
  `user_id` bigint,
  `login_name` string,
  `state` string,
  `create_at` string,
  `closed_at` string,
  `merged_at` string,
  `updated_at` string,
  `time_open_to_merge_seconds` bigint,
  `time_cretead_to_update_seconds` bigint)
PARTITIONED BY (
  `owner` string,
  `repo` string,
  `date` string)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY '\;'
STORED AS INPUTFORMAT
LOCATION
  's3://de-github-analytics-dev/processed/pull_request/'
</pre>

- **serverless BI service:** Amazon **QuickSight** has a serverless architecture that automatically scales to tens of thousands of users without the need to setup, configure, or manage your own servers.

## Get started
Setup local environment
1. Install `pyenv` - [guide](https://faun.pub/pyenv-multi-version-python-development-on-mac-578736fb91aa)
2. Set local environment to python 3.9 - `pyenv local 3.9.13`
3. Create python virtual environment - `python3 -m venv .venv`
4. Install dependencies - `pip3 install -r requirements.txt`

Set AWA Access
1. in terminal run command - aws configure
2.  enter account details

<pre>
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
</pre>

Deploy resources to cloud
1. navigate to IAC folder - cd /IAC
2. run : cdk synth -c env=dev , can set envirment in [app.py](https://github.com/yanivh/Github-Pull-Request-Analytics/blob/main/IAC/app.py)
<pre>
"snd": cdk.Environment(account="177806169472", region="eu-west-1"),
"dev": cdk.Environment(account="177806169472", region="eu-west-2"),
"prod": cdk.Environment(account="177806169472", region="us-west-1"),
</pre>
2. run : cdk deploy -c env=dev

Run Step Function
1. login into aws console 
2. navigate to Step Function service 
3. search for function name : **DE-SFN-GITHUB-DEV-PULL_REQUEST_LOADER**
4. start new execution

## Solution Architecture 

![alt text](https://github.com/yanivh/Github-Pull-Request-Analytics/blob/2fd8a2fdc3c02b90d697ed6b8474c0c28fbe441d/Solution_Architecture_diagram.jpeg)

- **Visualization :**

![alt text](https://github.com/yanivh/Github-Pull-Request-Analytics/blob/4085e7f8fca2c5137a7fd69d34abd482ea5eca7e/Visualization/viz_1.png)
![alt text](https://github.com/yanivh/Github-Pull-Request-Analytics/blob/4085e7f8fca2c5137a7fd69d34abd482ea5eca7e/Visualization/viz_2.png)
![alt text](https://github.com/yanivh/Github-Pull-Request-Analytics/blob/4085e7f8fca2c5137a7fd69d34abd482ea5eca7e/Visualization/viz_3.png)

