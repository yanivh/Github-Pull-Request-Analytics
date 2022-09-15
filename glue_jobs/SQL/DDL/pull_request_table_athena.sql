CREATE EXTERNAL TABLE `pull_request_pull_request`(
  `id` bigint,
  `number` bigint,
  `title` string,
  `user_id` bigint,
  `login_name` string,
  `state` string,
  `create_at` string,
  `closed_at` string,
  `merged_at` string,
  `open_to_merge_seconds` bigint,
  `time_open__seconds` bigint)
PARTITIONED BY (
  `owner` string,
  `repo` string,
  `date` string)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY '\;'
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://git-analytics/processed/pull_request/'
TBLPROPERTIES (
  'CrawlerSchemaDeserializerVersion'='1.0',
  'CrawlerSchemaSerializerVersion'='1.0',
  'UPDATED_BY_CRAWLER'='pull_request',
  'areColumnsQuoted'='false',
  'averageRecordSize'='154',
  'classification'='csv',
  'columnsOrdered'='true',
  'compressionType'='none',
  'delimiter'='\;',
  'objectCount'='1',
  'recordCount'='53',
  'sizeKey'='8207',
  'typeOfData'='file')