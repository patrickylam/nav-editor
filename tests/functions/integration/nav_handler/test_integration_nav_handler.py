# Copyright (c) 2017 lululemon athletica Canada inc.
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

import os, json
here = os.path.dirname(os.path.realpath(__file__))
from tight.core.test_helpers import expected_response_body

def test_get_method(app, dynamo_db_session):
    context = {}
    event = {
        'httpMethod': 'GET'
    }
    actual_response = app.nav_handler(event, context)
    actual_response_body = json.loads(actual_response['body'])
    expected_response = expected_response_body(here, 'expectations/test_get_method.yml', actual_response)
    assert actual_response['statusCode'] == 200, 'The response statusCode is 200'
    assert actual_response_body == expected_response, 'Expected response body matches the actual response body.'