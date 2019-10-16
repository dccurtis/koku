
from masu.processor.aws.aws_report_processor import AWSReportProcessor

if '__main__' in __name__:
    report_path = '/testing/pvc_dir/processing/acct10001/aws-local/_tmp_local_bucket/02c395ca-3f72-4b79-9d22-2440b1da00c8-cost-management-01.csv.gz'
    schema = 'acct10001'
    compression = 'GZIP_COMPRESSED'
    provider_id = 1
    processor = AWSReportProcessor
