from invoke import task
from os import environ
import os
from sys import exit
import subprocess
import shutil
import glob
import boto3
import yaml
import json


def sanity_check(ctx):
    if environ.get('ARTIFACT_DEPLOY_REGION') is None:
        exit("Environment variable ARTIFACT_DEPLOY_REGION not set")
    ctx.travis_pull_request = environ.get('TRAVIS_PULL_REQUEST')
    if ctx.travis_pull_request is None or ctx.travis_pull_request == 'false':
        print("NOT a pull request")
        if environ.get('TRAVIS_BRANCH') == 'master':
            ctx.travis_pull_request = 'master'
        else:
            exit(0)
    else:
        print("Found pull request number via environment variable: [TRAVIS_PULL_REQUEST={}]".format(
            ctx.travis_pull_request))


def init(ctx):
    ctx.artifact_deploy_region = environ.get('ARTIFACT_DEPLOY_REGION', 'us-west-2')
    ctx.github_base_url = "https://github.com"
    ctx.travis_base_url = "https://travis-ci.com"


def distribute(ctx, name, build_dir, metadata_file, env_name=None, tag=None):
    # NOTE: all TRAVIS_* vars exist in the travisCI build environment
    travis_repo_slug = environ.get('TRAVIS_REPO_SLUG', '')
    travis_commit_range = environ.get('TRAVIS_COMMIT_RANGE', '')
    travis_build_id = environ.get('TRAVIS_BUILD_ID', '')
    travis_job_number = environ.get('TRAVIS_JOB_NUMBER', '')
    travis_node_version = environ.get('TRAVIS_NODE_VERSION', '')

    meta_data_elements = [
        'pr_number={}'.format(ctx.travis_pull_request),
        'git_diff_url={}/{}/compare/{}'.format(ctx.github_base_url, travis_repo_slug, travis_commit_range),
        'pr_url={}/{}/pull/{}'.format(ctx.github_base_url, travis_repo_slug, ctx.travis_pull_request),
        'ci_build_url={}/{}/builds/{}'.format(ctx.travis_base_url, travis_repo_slug, travis_build_id),
        'ci_build_number={}'.format(travis_job_number),
        'ci_build_lang_version={}'.format(travis_node_version)
    ]

        # We will s3 sync all build assets to this folder
    if env_name:
        artifact_builds_s3_object_folder = "ecom/gtwy/translation/environments/{}/{}/{}".format(env_name, name, tag)
    else:
        tag = 'master' if ctx.travis_pull_request == 'master' else 'pr-{}'.format(ctx.travis_pull_request)
        artifact_builds_s3_object_folder = "ecom/gtwy/translation/distributions/{}/{}".format(name, tag)

    # # upload all except config
    ctx.run('aws --region {} s3 sync {} s3://{}/{} --content-encoding gzip --exclude {}/{}'.format(
        ctx.artifact_deploy_region,
        build_dir,
        ctx.artifact_deploy_s3_bucket,
        artifact_builds_s3_object_folder,
        build_dir,
        metadata_file))

    metadata = ','.join(meta_data_elements)
    # upload the config with metadata applied
    ctx.run('aws --region {} s3 cp {}/{} s3://{}/{}/{} --content-encoding gzip --metadata {} '.format(
        ctx.artifact_deploy_region,
        build_dir,
        metadata_file,
        ctx.artifact_deploy_s3_bucket,
        artifact_builds_s3_object_folder,
        metadata_file,
        metadata))

    return artifact_builds_s3_object_folder


@task
def test(ctx):
    here = os.path.dirname(os.path.realpath(__file__))
    with ctx.cd(here):
        ctx.run('py.test tests --confcutdir ./')


def build_tight_app(ctx):
    """
    Build the server side application.
    Finally, to support our deploy process we will name the resulting
    zip to the repository's short SHA1.
    :return:
    """
    """ Always start with a clean build space. """
    if os.path.isdir('./builds'):
        shutil.rmtree('./builds')
    """ We're regenerating the artifact and augmenting it. We will need the correct name. This should match the
    value for 'name' that is found in tight.yml """
    name = 'mobile-api-serverless'
    """ Make a default artifact """
    ctx.run('tight generate artifact')

    """ For good measure, copy over the config files. """
    ctx.run('cp ./tight.yml builds/')
    ctx.run('cp ./env.dist.yml builds/')
    """ Now compress it all """
    zips = glob.glob('./builds/*.zip')
    if len(zips) > 0:
        for zip in zips:
            os.remove(zip)
    zip_name = '{}/builds/{}'.format(os.getcwd(), ctx.rev)
    create_zip = ['zip', '-9', zip_name]
    subprocess.call(create_zip)
    artifact_dir = '{}/builds/{}-artifact/'.format(os.getcwd(), name)
    shutil.make_archive(zip_name, 'zip', root_dir=artifact_dir)
    shutil.rmtree(artifact_dir)


@task()
def json_to_yaml(ctx, path):
    with open(path) as source_file:
        data = yaml.load(source_file.read())

    with open(path.split('.json')[0] + '-xform.yaml', 'w') as yaml_file:
        yaml_file.write(yaml.safe_dump(data, default_flow_style=False))


@task()
def package(ctx):
    """
    Packaging consists of:
    1. Building the web app, since the tight app depends on the generated javascript.
    2. Build the tight app.
    3. Compress all of the files from the web app build. This is important to do after building the tight app
       since the tight app doesn't expect compressed js source.
    4. Distribute the tight app to the server side builds bucket location.
    5. Distribute the web app to the static client builds bucket location.
     The result is that the following artifacts / files will be in S3:
     contents of `./builds/` will be synced to:
     `lll-nonprod-src-artifacts-us-west-2/ecom/gtwy/translation/distributions/tight-app/pr-<PR_NUMBER>`
    :return:
    """
    """ We use the current commit's short SHA1 fingerprint to name the artifact. """
    ctx.rev = ctx.run('git rev-parse --short HEAD').stdout.strip()

    """ Perform sanity check to make sure that we can build safely and that we have some build related env vars set. """
    #sanity_check(ctx)
    init(ctx)

    """ Does a little more than what it says... Look at function body for more info :) """
    build_tight_app(ctx)

    """ Get ready to deploy the server side artifcacts, first. """
    ctx.artifact_deploy_s3_bucket = 'lll-nonprod-src-artifacts-us-west-2'
    distribution_key = distribute(ctx, 'tight-app', './builds', 'tight.yml')

    """ We indicate which was the last build by writing the current git short SHA to a file called 'latest' """
    s3_client = boto3.client('s3')
    s3_client.put_object(Body=bytes(ctx.rev, 'utf-8'), Key='{}/latest'.format(distribution_key), Bucket=ctx.artifact_deploy_s3_bucket)
