import os
import yaml
import hmac
import logging


log = logging.getLogger('webhook-deploy')


class DeploymentJob:
    def __init__(self, id, payload):
        self.id = id
        self.payload = payload


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


def run_deployment_job(job: DeploymentJob):
    # Make a temp directory
    # Clone repo into that directory (user running this webapp must have an ssh key registered on github?)
    # Build the source code in the cloned repo from a build config
    # Copy all (or only built files) files to the destination dir in config
    # Delete temp dir
    # Log all of this
    # Store the log and stuff somewhere, identified by the delivery id

    repo_name = job.payload['repository']['full_name']
    pushed_ref = job.payload['ref']
    log.debug(f'run_deployment_job: repo_name {repo_name}, pushed_ref {pushed_ref}')

    # TODO: check real repo names and pushed ref name format
    if repo_name == 'Kvark' and pushed_ref == 'production':
        log.info('Running deployment for Kvark')

    elif repo_name == 'API' and pushed_ref == 'production':
        log.info('Running deployment for API')

    else:
        log.info(f'Delivery {job.id} skipped, not configured for this repo/ref')


if __name__ == '__main__':
    secret = load_secret()
    print(verify_signature('testæøå', 'lol', secret))
