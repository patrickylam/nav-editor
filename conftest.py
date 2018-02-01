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

# content of conftest.py
import pytest, os, sys, importlib, yaml, json, boto3
here = os.path.dirname(os.path.realpath(__file__))
sys.path = [os.path.join(here, "app/vendored")] + sys.path

from tight.core.test_helpers import *

def pytest_sessionstart():
    os.environ['AWS_REGION'] = 'us-west-2'
    os.environ['NAME'] = 'nav-editor'
    os.environ['STAGE'] = 'dev'
    if 'CI' not in os.environ:
        os.environ['CI'] = 'False'
        os.environ['USE_LOCAL_DB'] = 'True'