# API  https://q8xm16pw72.execute-api.eu-west-1.amazonaws.com/Test1/sentiment?file=sample-13


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

    print(json.dumps(event))

    # get FileName from query  , file from API
    file_name = event["queryStringParameters"]["file"]
    jsonFileName = file_name + ".json"

    # construct the file path in bucket
    jsonFilePath = "transcripts/{}".format(jsonFileName)

    print(jsonFilePath)
    try:
        s3.get_object(Bucket=bucket_name, Key=jsonFilePath)
        file_exist = True
    except ClientError as e:
        print(e)
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
                "body": json.dumps("Other error 1  ")
            }

    if file_exist:
        try:
            # get the file from the bucket & read the content
            file_object = s3.get_object(Bucket=bucket_name, Key=jsonFilePath)
            # reading byte object data and converting to string to process the data
            # this is string data
            file_content = file_object["Body"].read().decode('utf-8')

            # read the transcripted full data as json format
            transcripts = json.loads(file_content)
            transcript_str = transcripts["results"]["transcripts"][0]["transcript"]

            client_sentiment = boto3.client("comprehend")
            response = client_sentiment.detect_sentiment(
                Text=transcript_str,
                LanguageCode="en"
            )

            # sentiment_scores = response["SentimentScore"]

            # if all ok return the content to user
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "transcript_str": transcript_str,
                    "Response": response,
                    # "sentiment_scores": sentiment_scores
                })

            }
        except Exception as e:
            # return the error
            return {
                "statusCode": 500,
                "body": json.dumps("Other error 2  ")

            }
