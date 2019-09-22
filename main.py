import os
import yaml
import hmac
import logging
import subprocess
from typing import Optional


log = logging.getLogger('webhook-deploy')


class DeploymentJob:
    def __init__(self, id: str, specification: dict):
        self.id = id
        self.specification = specification


class WebhookDeploy:
    def __init__(self):
        self._secret = self._load_secret()
        self._config = self._load_config()

    def _load_secret(self) -> bytes:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.txt')) as f:
            return f.readline().strip().encode('utf-8')

    def _load_config(self) -> dict:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')) as f:
            return yaml.load(f)

    def verify_signature(self, payload: str, signature: str) -> bool:
        payload_bytes = payload.encode('utf-8')
        digest = hmac.new(self._secret, payload_bytes, 'sha1')
        expected_signature = 'sha1=' + digest.hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    def get_deployment_specification(self, repository: str, ref: str) -> Optional[dict]:
        return next((d for d in self._config['deployments']
                     if d['repository'] == repository and d['ref'] == ref), None)


def run_deployment_job(job: DeploymentJob) -> None:
    log.info('Running deployment for ' + job.specification['name'])

    log_file_path = f'/var/log/webhook-deployments/{job.id}.log'
    log_file = open(log_file_path, 'w+')

    result = subprocess.run(['/bin/bash', job.specification['deploymentScript']],
                            encoding='utf-8', stdout=log_file, stderr=subprocess.STDOUT)
    log_file.close()

    if result.returncode == 0:
        log.info('Deployment succeeded')
    else:
        log.error(f'Deployment FAILED with error code {result.returncode}')

    log.info(f'Output from deployment script saved in {log_file_path}')


if __name__ == '__main__':
    wc = WebhookDeploy()
    payload = \
'''{
  "ref": "refs/heads/production",
  "repository": {
    "full_name": "TIHLDE/Kvark"
  }
}'''
    payload_bytes = payload.encode('utf-8')
    digest = hmac.new(wc._secret, payload_bytes, 'sha1')
    print('sha1=' + digest.hexdigest())

    # secret = load_secret()
    # print(verify_signature('testæøå', 'lol', secret))

    # f = open('testlol-out.txt', 'w+')
    # result = subprocess.run(['bash', 'testlol.bash'], encoding='utf-8',
    #                         stdout=f, stderr=subprocess.STDOUT)
    # # print(result)
    # print(f'return code: {result.returncode}')
    # print(f'stdout: """{result.stdout}"""')
    # # print(result.stderr)
