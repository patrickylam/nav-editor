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

from tight.providers.aws.clients import dynamo_db
import tight.providers.aws.controllers.lambda_proxy_event as lambda_proxy
db = dynamo_db.connect()

@lambda_proxy.get
def get_handler(*args, **kwargs):
    return {
        'statusCode': 200,
        'body': {
            'hello': 'world'
        }
    }

@lambda_proxy.post
def post_handler(*args, **kwargs):
    pass

@lambda_proxy.put
def put_handler(*args, **kwargs):
    pass

@lambda_proxy.patch
def patch_handler(*args, **kwargs):
    pass

@lambda_proxy.options
def options_handler(*args, **kwargs):
    pass

@lambda_proxy.delete
def delete_handler(*args, **kwargs):
    pass