# Github Analytics

GitHub Anlytics, pull new data about the Grafana repository into a database.

- **Visualizations:**
- **infrastructure as a code:** Infrastructure as Code (IaC) is the managing and provisioning of infrastructure through code instead of through manual processes. With IaC, configuration files are created that contain your infrastructure specifications, which makes it easier to edit and distribute configurations  
<pre>
 Github-Analytics -IAC
 IAC/S3 -  datalake storage
 IAC/glue/jobs - extract load , execute a python script
 IAC/glue/core - create IAM role's
 IAC/step_function - orcastrate the data ingestion.
</pre>

- **GitHub API:** using GitHub's REST API v3.
with knowing that every pull request an issue, but not every issue is a pull request. 
For this reason, "Issues" endpoints may return both issues and pull requests in the response. 
You can identify pull requests by the pull_request key. Be aware that the id of a pull request returned from "Issues" endpoints will be an issue id. To find out the pull request id, use the "List pull requests" endpoint.


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

- **Solution Architecture :**

![alt text](https://github.com/yanivh/Github-Pull-Request-Analytics/blob/2fd8a2fdc3c02b90d697ed6b8474c0c28fbe441d/Solution_Architecture_diagram.jpeg)

