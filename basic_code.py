# Libraries
import boto3
import uuid
import json


# Run when AWS Lamda Triggered
def lambda_handler(event, context):
    # convert argument event as json & prints
    print(json.dumps(event))

    # Extract first record from argument 'event'
    record = event['Records'][0]

    # Extract the name of bucket & key of uploaded audio file from record variable
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']

    # get only the name before the extention
    first_name, _ = s3object.rsplit('.', 1)

    # has s3bucket name, audio file key as string
    s3path = f's3://{s3bucket}/{s3object}'
    # Unique name for the transcribe job bu uuid module
    jobName = f'{s3object}--{str(uuid.uuid4())}'
    # path & name of output file 'text file'
    outputKey = f'transcripts/{first_name}.json'

    # boto3 client object
    client = boto3.client('transcribe')

    #To include speaker label also
    settings = {
        'ShowSpeakerLabels': True,
        'MaxSpeakerLabels': 10,  # Adjust as needed (2-10)

    }

    # for new transcribe job
    # jobname,language,location of media file, location of output
    response = client.start_transcription_job(
        TranscriptionJobName=jobName,
        LanguageCode='en-US',
        Media={'MediaFileUri': s3path},
        OutputBucketName=s3bucket,
        OutputKey=outputKey,
        Settings=settings
    )
    # convert AWS response to JSON string
    print(json.dump(response, default=str))

    # returns the dictionary with transcription name,key, job name
    return {
        'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
    }


