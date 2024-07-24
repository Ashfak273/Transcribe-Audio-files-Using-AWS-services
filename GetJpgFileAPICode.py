#this is the API for this code
#https://r6jzjrc8f5.execute-api.eu-west-1.amazonaws.com/get_file2?file=GRrwCnR1uV1QSfEuuGyn43iXJiCfELqOHxCWrrT7.jpg

import base64
import boto3


s3 = boto3.client('s3')

def lambda_handler(event, context):
    #get bucket name
    bucket_name = "audiototextbucket3"
    #get name of the file
    file_name = event ["queryStringParameters"]["file"]
    #get the object from the bucket by bucket_name,filename
    fileObj = s3.get_object(Bucket=bucket_name, Key=file_name)
    #file content from the body
    file_content = fileObj["Body"].read()

    # print
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Content-Disposition": "attachment; filename={}".format(file_name)
        },
        #converting the file to base64 due to the file not going to be sent normally so we have to transfrom
        "body": base64.b64encode(file_content),
        "isBase64Encoded": True
    }
