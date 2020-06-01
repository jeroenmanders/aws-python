import boto3
from botocore.exceptions import ClientError


class SesMailer(object):

    def __init__(self):
        pass

    def mail(self, sender, recipient, subject, body_text, body_html):
        CONFIGURATION_SET = "ConfigSet"
        AWS_REGION = "us-east-1"
        CHARSET = "UTF-8"
        client = boto3.client('ses', region_name=AWS_REGION)

        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': subject,
                    },
                },
                Source=sender,
                #ConfigurationSetName=CONFIGURATION_SET,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])