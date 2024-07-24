import boto3
import uuid
import json
import base64
from botocore.exceptions import ClientError

s3=boto3.client('s3')

def lambda_handler(event, context):

    # place the bucket name
    bucket_name = "audiototextbucket3"

    # get FileName from query  , file
    file_name = event["queryStringParameters"]["file"]
    jsonFileName = file_name + ".json"

    # construct the file path in bucket
    jsonFilePath = "transcripts/{}".format(jsonFileName)

    try:
        #CHeck the file is in the path or not
        s3.get_object(Bucket=bucket_name, Key=jsonFilePath)
        file_exist = True
    except s3.exception.NoSuchKey:
        file_exist = False

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

    else:
        audioFileName1 = file_name + ".mp3"
        audioFileName2 = file_name + ".wav"
        audioFile1Path = f's3://{bucket_name}/{audioFileName1}'
        audioFile2Path = f's3://{bucket_name}/{audioFileName2}'

        try:
            s3.head_object(Bucket=bucket_name, Key=audioFile1Path)
            audioFile1_exist = True
        except s3.exception.NoSuchKey:
            audioFile1_exist = False

        try:
            s3.head_object(Bucket=bucket_name, Key=audioFile2Path)
            audioFile2_exist = True
        except s3.exception.NoSuchKey:
            audioFile2_exist = False

        if audioFile1_exist:

            # Unique name for the transcribe job bu uuid module
            jobName = f'{audioFileName1}--{str(uuid.uuid4())}'
            # path & name of output file 'text file'
            outputKey = f'transcripts/{file_name}.json'

            # boto3 client object
            client = boto3.client('transcribe')

            # for new transcribe job
            # jobname,language,location of media file, location of output
            response = client.start_transcription_job(
                TranscriptionJobName=jobName,
                LanguageCode='en-US',
                Media={'MediaFileUri': audioFile1Path},
                OutputBucketName=bucket_name,
                OutputKey=outputKey
            )
            # convert AWS response to JSON string
            print(json.dump(response, default=str))

            # returns the dictionary with transcription name,key, job name
            return {
                'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
            }

        elif audioFile2_exist:

            # Unique name for the transcribe job bu uuid module
            jobName = f'{audioFileName2}--{str(uuid.uuid4())}'
            # path & name of output file 'text file'
            outputKey = f'transcripts/{file_name}.json'

            # boto3 client object
            client = boto3.client('transcribe')

            # for new transcribe job
            # jobname,language,location of media file, location of output
            response = client.start_transcription_job(
                TranscriptionJobName=jobName,
                LanguageCode='en-US',
                Media={'MediaFileUri': audioFile2Path},
                OutputBucketName=bucket_name,
                OutputKey=outputKey
            )
            # convert AWS response to JSON string
            print(json.dump(response, default=str))

            # returns the dictionary with transcription name,key, job name
            return {
                'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
            }
        else:
            # No audio file found
            return {
                'statusCode': 404,
                'body': json.dumps('There is no such file')
            }













