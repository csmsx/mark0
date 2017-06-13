#!/usr/bin/env python

import boto3

import lib.collect.backends.errors as errors
import lib.collect.config as config


RESERVED_CHARACTER = config.DYNAMODB_KEY_RESERVED_CHARACTER
BUCKET = config.S3_BUCKET


def setup():
    db = boto3.resource('dynamodb')
    table = db.create_table(
        TableName=config.DYNAMODB_TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'deployment_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'ts',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'deployment_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'ts',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=config.DYNAMODB_TABLE_NAME)


def record(payload):
    db = boto3.resource('dynamodb')
    table = db.Table(config.DYNAMODB_TABLE_NAME)
    try:
        hash_key = __valid_hash(payload)
        data = payload
        data['deployment_id'] = hash_key
        table.put_item(Item=data)
    except Exception as e:
        raise errors.BackendRecordError(e)


def backups(files = [], keys = []):
    try:
        s3 = boto3.client('s3')
        for idx, f in enumerate(files):
            key = keys[idx]
            with open(f, 'rb') as fh:
                s3.put_object(Body=fh,
                              Bucket=BUCKET,
                              Key=key,
                              ACL='authenticated-read',
                              StorageClass='STANDARD')
    except Exception as e:
        raise errors.BackendBackupError(e)


def __valid_hash(payload):
    # Hash key within 2048 bytes
    '''
    Valid payload:
    - Dictionary with minimum entries as follows:
    - {
        "api": 0,
        "client": {
          "v": 0,
          "i": "",
          "m": "",
        },
        "state": {},
        "ts": "",
      }
    '''
    try:
        api = payload['api']
        client_version = payload['client']['v']
        client_id = payload['client']['i']
        client_model = payload['client']['m']
        state = payload['state']
        ts = payload['ts']
        hash_key = RESERVED_CHARACTER.join([
            str(client_id),
            str(client_version),
            str(client_model),
            str(api),
        ])
        return hash_key
    except KeyError as e:
        raise errors.BackendInvalidPayloadError(e)


def __escape_forbidden(string):
    return string.replace(RESERVED_CHARACTER, '__SHARP__')


def __unescape_forbidden(string):
    return string.replace('__SHARP__', RESERVED_CHARACTER)


if __name__ == '__main__':
    setup()
