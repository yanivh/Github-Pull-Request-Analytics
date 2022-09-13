import logging
import math
import os
import sys
from datetime import date, timedelta
from types import SimpleNamespace
import re

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

    def __init__(self, secret_name: str):
        self.secret_name = secret_name
        self.session = None
        self.config = None

    def __enter__(self):
        self.get_session()
        return self

    def get_session(self):
        logger.info("Getting Connection Info")
        self.config = helper.get_aws_secret(self.secret_name)

        logger.info(f"Connecting to Rest API: {self.config.host}")
        self.session = requests.Session()
        self.session.auth = (self.config.username, self.config.password)
        self.session.post(self.config.host)
        return self

    def get(self, query):
        return self.session.get(f"{self.config.host}?{query}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()


class ServiceMonitorLoader:
    def __init__(
        self, rest_api_secret: str, redshift_secret: str, redshift_schema: str, redshift_table: str, date: date
    ):
        self.redshift_secret = redshift_secret
        self.redshift_schema = redshift_schema
        self.redshift_table = redshift_table
        self.date = date.strftime("%Y-%m-%d")
        self.api = RestAPI(rest_api_secret).get_session()
        self.page_size = 100

        self.data = []

    def _get_query_from(self, page):
        return page * self.page_size

    def _get_page_count(self):
        resp = self.api.get(f"DateUpdatedStart={self.date}&PaginationSize=1")
        total_count = resp.json()["TotalCount"]

        return math.ceil(total_count / self.page_size)

    def _get_page(self, query_from: int):
        resp = self.api.get(f"DateUpdatedStart={self.date}&PaginationSize={self.page_size}&QueryFrom={query_from}")
        self.data += resp.json()["Results"]

    def get_data(self):
        page_count = self._get_page_count()
        for page in range(page_count):
            self._get_page(query_from=self._get_query_from(page))

    def explode_array(self, array_key: str):
        data = []
        for row in self.data:
            array = row[array_key]

            if len(array) == 1:
                logging.warning(f"API message does not have valid payload {row}")
                continue

            if array[1]["QuestionName"] != "Compass Code":
                raise Exception("API response does not match expected schema")

            # Remove the array from the dictionary
            row.pop(array_key, None)

            # Add the attay to the dictionary as new keys
            data.append({**row, **array[0], "CompassUnitId": array[1]["Caption"]})

        self.data = data

    def truncate_staging_table(self):
        with helper.RedshiftHandler(self.redshift_secret) as rs:
            rs.execute(f'TRUNCATE "{self.redshift_schema}"."{self.redshift_table}";')

    def load_staging_table(self):
        # Get column order from Redshift
        with helper.RedshiftHandler(self.redshift_secret) as rs:
            table_schema = rs.get_table_schema(schema=self.redshift_schema, table=self.redshift_table)
            index_map = {calue: idx for idx, calue in enumerate(table_schema.keys())}

        # Generate values section
        values = []
        for row in self.data:
            # Sort the dictionary key based on redshift table schema
            sorted_row = dict(sorted(row.items(), key=lambda x: index_map[x[0].lower()]))
            string_row = str(tuple((value) for value in sorted_row.values()))
            values.append(string_row.replace("None", "null"))

        # Load data into redshift
        with helper.RedshiftHandler(self.redshift_secret) as rs:
            rs.execute(f'INSERT INTO "{self.redshift_schema}"."{self.redshift_table}" VALUES {", ".join(values)};')


def get_pullRequest(page,filter_list, end_date_day):


    # List object
    list_r = r.json()

    # get only pull request
    for l in list_r:
        if 'pull_request' in l and end_date_day in l['updated_at']:
            filter_list.append(l)


    return filter_list



def simple ():
    import requests
    import os
    from pprint import pprint
    import json

    token = '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'
    owner = "grafana"
    repo = "grafana"
    query_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    'YYYY-MM-DDTHH:MM:SSZ'

    start_date = '2022-09-10T00:00:00'
    end_date = '2022-09-13T23:59:59'
    end_date_day = '2022-09-13'

    params = {
        "state": "all",
        "since": f"{start_date}",
        "sort":"updated",
        "direction":"asc"
    }
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers, params=params)

    filter_list = []

    # if 'next' in r.links:
    #     page_next = r.links['next']

    if 'last' in r.links:
        last=r.links['last']
        number_of_pages=re.search(r'&page=(\d+)', last['url']).group(1)
        # {'url': 'https://api.github.com/repositories/15111821/issues?state=all&since=2022-09-10T00%3A00%3A00&sort=updated&direction=asc&page=11', 'rel': 'last'}
        print (last)



    print (1)


if __name__ == "__main__":

    simple()
    print (1)

    args = load_glue_contex()

    if args.FullLoad == "True":
        date = date(2021, 8, 1)
        logger.info(f"Full load start_date:{date}")
    else:
        date = date.today() - timedelta(days=5)
        logger.info(f"Incremental load start_date:{date}")

    service_monitor_loader = ServiceMonitorLoader(
        rest_api_secret=args.ServiceMonitorSecret,
        redshift_secret=args.RedshiftSecret,
        redshift_schema="stg",
        redshift_table="fct_nps_servicemonitor",
        date=date,
    )
    service_monitor_loader.get_data()
    service_monitor_loader.explode_array(array_key="Responses")
    service_monitor_loader.truncate_staging_table()
    service_monitor_loader.load_staging_table()
