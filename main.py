import os
import yaml
import hmac
import time
import multiprocessing as mp


def load_secret() -> bytes:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.txt')) as f:
        return f.readline().strip().encode('utf-8')


def load_config() -> dict:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')) as f:
        return yaml.load(f)


def verify_signature(payload: str, signature: str, secret: bytes) -> bool:
    payload_bytes = payload.encode('utf-8')
    digest = hmac.new(secret, payload_bytes, 'sha1')
    expected_signature = 'sha1=' + digest.hexdigest()
    return hmac.compare_digest(expected_signature, signature)


def do_deploy(config, delivery_id, payload):
    # Sequence:
    # Check if repo name is in config
    # Check if pushed ref is branch for that repo in config
    # Make a temp directory
    # Clone repo into that directory (user running this webapp must have an ssh key registered on github?)
    # Build the source code in the cloned repo from a build config
    # Copy all (or only built files) files to the destination dir in config
    # Delete temp dir
    # Log all of this
    # Store the log and stuff somewhere, identified by the delivery id
    repo_name = payload['repository']['full_name']
    pushed_ref = payload['ref']
    deployment_config = None
    for deployment in config['deployments']:
        if deployment['repository'] == repo_name and deployment['branch'] == pushed_ref:
            deployment_config = deployment

    if deployment_config:
        pass
    else:
        print('No matching config found')


def real_do_deploy(delivery_id, repo, ref, config):
    # Make a temp directory
    # Clone repo into that directory (user running this webapp must have an ssh key registered on github?)
    # Build the source code in the cloned repo from a build config
    # Copy all (or only built files) files to the destination dir in config
    # Delete temp dir
    # Log all of this
    # Store the log and stuff somewhere, identified by the delivery id
    pass


if __name__ == '__main__':
    secret = load_secret()
    print(verify_signature('testæøå', 'lol', secret))
