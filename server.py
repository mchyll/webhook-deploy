from main import WebhookDeploy, DeploymentJob, run_deployment_job
from aiohttp import web
import json
import logging
import sys
import threading
import queue


wd = WebhookDeploy()

log_stdout_hander = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter('%(name)s: [%(levelname)s] %(message)s')
log_stdout_hander.setFormatter(log_formatter)
logging.getLogger().addHandler(log_stdout_hander)
log = logging.getLogger('webhook-deploy')
log.setLevel(logging.INFO)

job_queue = queue.Queue()
worker_running = True


async def github_webhook_handle(req: web.Request) -> web.Response:
    try:
        payload = await req.text()
        signature = req.headers['X-Hub-Signature']
        delivery_id = req.headers['X-GitHub-Delivery']
        event_type = req.headers['X-GitHub-Event']

        if wd.verify_signature(payload, signature):
            if event_type == 'ping':
                log.info('Got ping event')
                return web.Response(status=200)

            elif event_type == 'push':
                payload_dict = json.loads(payload)
                repo_name = payload_dict['repository']['full_name']
                pushed_ref = payload_dict['ref']
                spec = wd.get_deployment_specification(repo_name, pushed_ref)

                if spec is None:
                    log.info(f'Delivery {delivery_id} skipped, not configured for repo/ref {repo_name} {pushed_ref}')
                    return web.Response(status=404, text=f'Delivery skipped, not configured for this repo/ref.')

                else:
                    log.info(f'Enqueueing job for delivery with id {delivery_id}')
                    job_queue.put(DeploymentJob(delivery_id, spec))
                    return web.Response(status=200, text=f'Delivery accepted and job enqueued.')

        else:
            log.warning(f'Invalid signature from {req.remote}')
            return web.Response(status=403)

    except json.decoder.JSONDecodeError as ex:
        log.error(f'JSON decode error: {ex.msg} from {req.remote}')
        return web.Response(status=400)

    except KeyError as ex:
        log.error(f'Key error: {ex} from {req.remote}')
        return web.Response(status=400)


def worker() -> None:
    log.info('Worker started')

    while worker_running:
        try:
            job = job_queue.get(timeout=5)
            run_deployment_job(job)
        except queue.Empty:
            pass


log.info('Webhook Deploy server starting')

worker_thread = threading.Thread(target=worker, name='DeploymentWorkerThread')
worker_thread.start()

app = web.Application()
app.add_routes([web.post('/github-webhook', github_webhook_handle)])

web.run_app(app, port=wd._config['serverPort'], print=None)

log.info('Webhook Deploy server stopping')
worker_running = False
worker_thread.join()
