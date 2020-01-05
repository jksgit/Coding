#!/usr/local/bin/python3
import json
import boto3
import os
import re
s3 = boto3.resource('s3')
client = boto3.client('s3')

  def convertColumntoLowwerCaps(obj):
    for key in obj.keys():
        new_key = re.sub(r'[\W]+', '', key.lower())
        v = obj[key]
        if isinstance(v, dict):
            if len(v) > 0:
                convertColumntoLowwerCaps(v)
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj

  def flatten_json(y):
      out = {}

      def flatten(x, name=''):
          if type(x) is dict:
              for a in x:
                  flatten(x[a], name + a + '.')
          elif type(x) is list:
              for a in x:
                  flatten(a, name)
          else:
              out[name[:-1]] = x

      flatten(y)
      return out

  def lambda_handler(event, context):

      bucket = event['Records'][0]['s3']['bucket']['name']
      key = event['Records'][0]['s3']['object']['key']
      try:
            client.download_file(bucket, key, '/tmp/file.json')
            with open('/tmp/file.json', 'rb') as file:
                for object in file:
                        record = json.loads(object,object_hook=convertColumntoLowwerCaps)
                        flatrec = flatten_json(record)
                        i = 1
                        for res in record['resources']:
                            flat = {'resources.'+k: v for k, v in flatten_json(res).items()}
                            mer = {**flatrec, **flat}
                            with open('/tmp/out.json', 'w') as output: output.write(json.dumps(mer))
                            newkey = 'flatfiles/' +str(i)+ key.replace("/", "")
                            i+=1
                            client.upload_file('/tmp/out.json', bucket,newkey)
                            print('Uploaded object {} to bucket {}'.format(newkey, bucket))
      except Exception as e:
            print(e)
            print('Error copying object {} from bucket {}'.format(key, bucket))
            raise e
