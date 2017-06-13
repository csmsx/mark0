#!/usr/bin/env python

import boto3

import lib.collect.backends.errors as errors
import lib.collect.config as config


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
    pass


def backups(files = []):
    pass


if __name__ == '__main__':
    setup()
