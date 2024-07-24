# API
# https://r6jzjrc8f5.execute-api.eu-west-1.amazonaws.com/get_file2?file=sample-4

# helps to interect with AWS services in python
import boto3
# this library helps to encode data to transfer over network
import base64

import json
from botocore.exceptions import ClientError

# interact with AWS service
s3 = boto3.client('s3')


def lambda_handler(event, context):
    # place the bucket name
    bucket_name = "audiototextbucket3"

    # get FileName from query  , file
    file_name = event["queryStringParameters"]["file"]
    jsonFileName = file_name + ".json"

    # construct the file path in bucket
    jsonFilePath = "transcripts/{}".format(jsonFileName)

    try:
        s3.get_object(Bucket=bucket_name, Key=jsonFilePath)
        file_exist = True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            file_exist = False
            return {
                "statusCode": 500,
                "body": json.dumps(f"There is no such {jsonFileName} file ")
            }
        else:
            # Handle other exceptions or log the error
            return {
                "statusCode": 500,
                "body": json.dumps(f"Error: {str(e)}")
            }

    if file_exist:
        try:
            # get the file from the bucket & read the content
            file_object = s3.get_object(Bucket=bucket_name, Key=jsonFilePath)
            file_content = file_object["Body"].read()

            # if all ok return the content to user
            return {
                "statusCode": 200,
                "headers": {
                    "Content_Type": "application/json",
                    "Content-Disposition": "attachment; filename = {}".format(jsonFileName)
                },
                # Also convert the file to base64
                "body": base64.b64encode(file_content).decode('utf-8'),  # Decoding to string
                "isBase64Encoded": True
            }
        except Exception as e:
            # return the error
            return {
                "statusCode": 500,
                "body": str(e)
            }





