 # -*- coding: utf-8 -*-
# MinIO Python Library for Amazon S3 Compatible Cloud Storage,
# (C) 2015 MinIO, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase

from nose.tools import eq_

import mock
from minio import Minio
from minio.api import _DEFAULT_USER_AGENT
from minio.error import InvalidArgumentError

from .minio_mocks import MockConnection, MockResponse

class GetBucketNotificationTest(TestCase):
    @mock.patch('urllib3.PoolManager')
    def test_notification_config_filterspec_is_valid_7(self, mock_connection):
        mock_data="""<?xml version="1.0"?>
<NotificationConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <QueueConfiguration>
        <Id></Id>
        <Filter>
            <S3Key>
                <FilterRule>
                    <Name>prefix</Name>
                    <Value>img</Value>
                </FilterRule>
                <FilterRule>
                    <Name>suffix</Name>
                    <Value>.jpg</Value>
                </FilterRule>
            </S3Key>
        </Filter>
        <Event>s3:ObjectCreated:*</Event>
        <Queue>arn:minio:sqs::6ccc8843-d78d-49e8-84c4-3734a4af9929:webhook</Queue>
    </QueueConfiguration>
</NotificationConfiguration>
"""
        mock_server = MockConnection()
        mock_connection.return_value = mock_server
        mock_server.mock_add_request(
            MockResponse(
                'GET',
                'https://localhost:9000/my-test-bucket/?notification=',
                {'User-Agent': _DEFAULT_USER_AGENT}, 200,
                content=mock_data.encode('utf-8')
            )
        )
        client = Minio('localhost:9000')
        response = client.get_bucket_notification('my-test-bucket')
        
        expected={
            'QueueConfigurations': [
                {
                    'Id': None, 
                    'Arn': 'arn:minio:sqs::6ccc8843-d78d-49e8-84c4-3734a4af9929:webhook', 
                    'Events': ['s3:ObjectCreated:*'], 
                    'Filter': [
                        {'Key': {'FilterRules': [
                            {'Name': 'prefix', 'Value': 'img'}, 
                            {'Name': 'suffix', 'Value': '.jpg'}
                        ]}}
                    ]
                }
            ]
        }
        eq_(expected,response)
