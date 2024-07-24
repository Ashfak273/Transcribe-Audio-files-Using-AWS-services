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

    # get FileName from query  , file from API
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
            # reading byte object data and converting to string to process the data
            file_content = file_object["Body"].read().decode('utf-8')

            # read the transcripted full data as json format
            transcripts = json.loads(file_content).get("results", {}).get("transcripts", [])
            conversation = []
            conversation.append(transcripts)
            formatted_conversation = conversation[0]

            # read the conversation full data as json format
            result = json.loads(file_content).get("results", {}).get("items", {})
            conversation3 = []


            #this loop save the every word with the readable format in a list
            for item in result:
                conversation3.append({
                    "type": item["type"],
                    #to avoide Keyerror we use .get() in dictionery, also if confidence not present it return empty value
                    "confidence": item["alternatives"][0].get("confidence", ""),
                    "content": item["alternatives"][0].get("content", ""),
                    "start_time": item.get("start_time", ""),
                    "end_time": item.get("end_time", ""),
                    "speaker_label": item.get("speaker_label", "")
                })

            current_speaker = None
            #main Dictionary
            current_sentence = {"content": "", "start_time": 0.4, "end_time": None, "confidence": []}

            for item in conversation3:
                if current_speaker is None:
                    current_speaker = item["speaker_label"]

                if current_speaker == item["speaker_label"]:
                    #this add every word
                    current_sentence["content"] += " " + item["content"]
                    #overwrite end_time
                    current_sentence["end_time"] = item["end_time"]
                    #append every value to list inside dictionary
                    current_sentence["confidence"].append(float(item["confidence"]))
                else:
                    # Add the completed sentence to the formatted conversation after transcripts
                    mean_confidence = sum(current_sentence["confidence"]) / len(current_sentence["confidence"])
                    formatted_conversation.append({
                        "type": "pronunciation",
                        "confidence": str(mean_confidence),
                        #strip() to remove extra white spaces
                        "content": current_sentence["content"].strip(),
                        "start_time": current_sentence["start_time"],
                        "end_time": current_sentence["end_time"],
                        "speaker_label": current_speaker
                    })

                    # Reset for the new speaker
                    current_sentence = {"content": item["content"], "start_time": item["start_time"],
                                        "end_time": item["end_time"], "confidence": [float(item["confidence"])]}
                    current_speaker = item["speaker_label"]

            # Add the last sentence to the conversation if next speaker is nt available
            if current_speaker is not None:
                mean_confidence = sum(current_sentence["confidence"]) / len(current_sentence["confidence"])
                formatted_conversation.append({
                    "type": "pronunciation",
                    "confidence": str(mean_confidence),
                    "content": current_sentence["content"].strip(),
                    "start_time": current_sentence["start_time"],
                    "end_time": current_sentence["end_time"],
                    "speaker_label": current_speaker
                })

            # if all ok return the content to user
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Content-Disposition": "attachment; filename = {}".format(jsonFileName)
                },
                #indent to make output humen readable like in vertical manner insted of horizontel
                "body": json.dumps(formatted_conversation, indent=2),  # Convert the conversation to JSON string
                "isBase64Encoded": False
            }
        except Exception as e:
            # return the error
            return {
                "statusCode": 500,
                "body": str(e)
            }
