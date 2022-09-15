import logging
import os
import sys
from datetime import date, timedelta
from types import SimpleNamespace
import json

import boto3
import requests

logger = logging.getLogger("mbition")
logger.setLevel(logging.INFO)
logger.debug("main message")

def load_glue_contex():
    if "GLUE_PYTHON_VERSION" in os.environ:
        from awsglue.utils import getResolvedOptions

        args = getResolvedOptions(sys.argv, ["ServiceMonitorSecret", "RedshiftSecret", "FullLoad"])
    else:
        args = {
            "ServiceMonitorSecret": "ServiceMonitorSecret",
            "RedshiftSecret": "DE-SEC-C9-DEV-REDSHIFT_CLUSTER",
            "FullLoad": "False",
        }

    return SimpleNamespace(**args)


class RestAPI:
    """This class provides a wrapper around Request library which is used for RestAPI communication."""

    def __init__(self):
        #  TODO: Get Token from Aws secrete manager
        self.token = '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'
        self.query_url = f"https://api.github.com/repos"
        self.headers = {'Authorization': f'token {self.token}'}

    def get_int_request(self, owner, repo, start_date, page_size):
        logger.info("Getting Connection Info")
        query = f"{self.query_url}/{owner}/{repo}/issues"
        params = {
            "state": "all",
            "since": f"{start_date}",
            "sort": "updated",
            "direction": "asc",
            "per_page": f"{page_size}"
        }

        response = requests.get(query, headers=self.headers, params=params)

        return response

    def get(self, url):
        res = requests.get(f"{url}", headers=self.headers)
        return res


class GitLoader:
    def __init__(self,
                 rest_api_secret: str,
                 git_owner: str,
                 git_repo: str
                 ):
        self.git_owner = git_owner
        self.git_repo = git_repo
        self.api = RestAPI()
        self.s3_resource = boto3.resource("s3")
        self.s3_client = boto3.client("s3")
        self.data = []

    def _get_query_from(self, page):
        return page * self.page_size

    def _get_page(self, query_from: int):
        resp = self.api.get(f"DateUpdatedStart={self.date}&PaginationSize={self.page_size}&QueryFrom={query_from}")
        self.data += resp.json()["Results"]

    def get_pull_requests_data(self, start_date: date, end_date: date, per_page: int):
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        next_page = False
        last_page = False

        init_resp = self.create_init_request(per_page)
        self.get_pull_request(init_resp, self.data, start_date)

        last_page, next_page = self.get_pagination_info(init_resp)
        resp = init_resp

        #  iterate till last page
        while next_page:
            if 'next' in resp.links:
                print(resp.links['next']['url'])
                resp = self.api.get(resp.links['next']['url'])
                self.get_pull_request(resp, self.data, end_date)
                last_page, next_page = self.get_pagination_info(resp)

    @staticmethod
    def get_pull_request(results, filter_list, end_date_day):

        # List object
        _results = results.json()

        # get only pull request type
        # get only with specific date in updated_at
        for result in _results:
            if 'pull_request' in result and end_date_day in result['updated_at']:
                filter_list.append(result)

        return filter_list

    def create_init_request(self, per_page):
        resp = self.api.get_int_request(self.git_owner, self.git_repo, start_date, per_page)
        return resp

    @staticmethod
    def get_pagination_info(resp):
        last_page = False
        next_page = False

        if 'last' in resp.links:
            last_page = True
        if 'next' in resp.links:
            next_page = True

        return last_page, next_page

    def save_result_to_file(self, owner, repo,start_date, type='pull_request'):
        file_name = f'{type}_{owner}_{repo}_{start_date}.json'
        with open(file_name, 'w', encoding='UTF-8') as fout:
            json.dump(self.data, fout)
        return file_name

    def save_result_to_s3(self, owner, repo, file_name , start_date, type='pull_request'):

        bucket = 'git-analytics'
        key = f'{type}/{owner}/{repo}/date={start_date}/{file_name}'
        with open(file_name, 'rb') as data:
            self.s3_client.upload_fileobj(data, bucket, key)


if __name__ == "__main__":

    start_date = date(2022, 9, 14)
    end_date = date(2022, 9, 14)
    git_owner = 'grafana'
    git_repo = 'grafana'

    args = load_glue_contex()

    git_loader = GitLoader(
        rest_api_secret=args.ServiceMonitorSecret,
        git_owner=git_owner,
        git_repo= git_repo
    )

    git_loader.get_pull_requests_data(start_date=start_date,
                                      end_date=end_date,
                                      per_page=100)

    file_name = git_loader.save_result_to_file(git_owner, git_repo, start_date)
    git_loader.save_result_to_s3(git_owner, git_repo, file_name, start_date)


