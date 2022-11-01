import os
import yaml
import hmac
import logging
import subprocess
from typing import Optional, List


log = logging.getLogger('webhook-deploy')


class DeploymentSpecification:
    def __init__(self, name: str, repository: str, ref: str, deployment_script: str):
        self.name = name
        self.repository = repository
        self.ref = ref
        self.deployment_script = deployment_script


class Config:
    def __init__(self, server_port: int, temp_dir: str, deployment_specifications: List[DeploymentSpecification]):
        self.server_port = server_port
        self.temp_dir = temp_dir
        self.deployment_specifications = deployment_specifications


class DeploymentJob:
    def __init__(self, id: str, specification: dict):
        self.id = id
        self.specification = specification


class WebhookDeploy:
    def __init__(self, config, secret):
        self._secret = secret
        self._config = config

    def verify_signature(self, payload: str, signature: str) -> bool:
        payload_bytes = payload.encode('utf-8')
        digest = hmac.new(self._secret, payload_bytes, 'sha1')
        expected_signature = 'sha1=' + digest.hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    def has_repository_specification(self, repository: str) -> bool:
        return any(d.repository == repository for d in self._config.deployment_specifications)

    def get_deployment_specification(self, repository: str, ref: str) -> Optional[DeploymentSpecification]:
        return next((d for d in self._config['deployments']
                     if d['repository'] == repository and d['ref'] == ref), None)


def load_secret(path=None) -> bytes:
    if path is None:
        path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'secret.txt')

    with open(path) as f:
        return f.readline().strip().encode('utf-8')


def load_config(path=None) -> Config:
    if path is None:
        path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'config.yml')

    with open(path) as f:
        y = yaml.safe_load(f)
        conf = Config(server_port=y['serverPort'],
                      temp_dir=y['tempDir'],
                      deployment_specifications=[])
        for spec in y['deployments']:
            conf.deployment_specifications.append(DeploymentSpecification(
                name=spec['name'], repository=spec['repository'],
                ref=spec['ref'], deployment_script=spec['deployment_script']))
        return conf


def run_deployment_job(job: DeploymentJob, config: Config) -> None:
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
