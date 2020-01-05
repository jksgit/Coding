import base64
import json
import logging
import zlib
import os
import boto3

class MailerSqsQueueIterator(object):
    # Copied from custodian to avoid runtime library dependency
    msg_attributes = ['sequence_id', 'op', 'ser']

    def __init__(self, aws_sqs, queue_url, logger, limit=0, timeout=10):
        self.aws_sqs = aws_sqs
        self.queue_url = queue_url
        self.limit = limit
        self.logger = logger
        self.timeout = timeout
        self.messages = []

    # this and the next function make this object iterable with a for loop
    def __iter__(self):
        return self

    def __next__(self):
        if self.messages:
            return self.messages.pop(0)
        response = self.aws_sqs.receive_message(
            QueueUrl=self.queue_url,
            WaitTimeSeconds=self.timeout,
            MaxNumberOfMessages=3,
            MessageAttributeNames=self.msg_attributes)

        msgs = response.get('Messages', [])
        self.logger.debug('Messages received %d', len(msgs))
        for m in msgs:
            self.messages.append(m)
        if self.messages:
            return self.messages.pop(0)
        raise StopIteration()

    next = __next__  # python2.7

DATA_MESSAGE = "maidmsg/1.0"
logger = logging.getLogger('custodian.queue')
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logging.getLogger('botocore').setLevel(logging.WARNING)

def process_sqs_message(encoded_sqs_message):
    client = boto3.client('s3')
    bucket = os.environ['bucket']
    body = encoded_sqs_message['Body']
    try:
        body = json.dumps(json.loads(body)['Message'])
    except ValueError:
        pass
    sqs_message = json.loads(zlib.decompress(base64.b64decode(body)))
    key = 'CustodianLogs/'+sqs_message['account_id']+'/'+sqs_message['policy']['name']+'/'+str(sqs_message['execution_start'])+'.json'

    with open('/tmp/out.json', 'w') as output:
        output.write(json.dumps(sqs_message))
    client.upload_file('/tmp/out.json', bucket, key)

def lambda_handler(event, context):
    receive_queue = os.environ['queue_url']

    logger.info("Downloading messages from the SQS queue.")
    aws_sqs = boto3.client('sqs')
    sqs_messages = MailerSqsQueueIterator(aws_sqs, receive_queue, logger)

    sqs_messages.msg_attributes = ['mtype', 'recipient']
    for sqs_message in sqs_messages:
        logger.debug(
            "Message id: %s received %s" % (
                sqs_message['MessageId'], sqs_message.get('MessageAttributes', '')))
        msg_kind = sqs_message.get('MessageAttributes', {}).get('mtype')
        if msg_kind:
            msg_kind = msg_kind['StringValue']
        if not msg_kind == DATA_MESSAGE:
            warning_msg = 'Unknown sqs_message or sns format %s' % (sqs_message['Body'][:50])
            logger.warning(warning_msg)
        process_sqs_message(sqs_message)
        logger.debug('Processed sqs_message')
    return
