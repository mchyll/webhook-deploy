from main import verify_signature, load_config, load_secret, DeploymentJob, run_deployment_job
from aiohttp import web
import json
import logging
import sys
import threading
import queue


__config = load_config()
__secret = load_secret()

__stdout_hander = logging.StreamHandler(sys.stdout)
__formatter = logging.Formatter(
    '%(asctime)s %(name)s: [%(levelname)s] %(message)s')
__stdout_hander.setFormatter(__formatter)
logging.getLogger().addHandler(__stdout_hander)
log = logging.getLogger('webhook-deploy')
log.setLevel(logging.INFO)

__job_queue = queue.Queue()


async def github_webhook_handle(req: web.Request):
    try:
        payload = await req.json()
        signature = req.headers['X-Hub-Signature']
        delivery_id = req.headers['X-GitHub-Delivery']
        event_type = req.headers['X-GitHub-Event']

        if verify_signature(payload, signature, __secret):
            if event_type == 'ping':
                log.info('Got ping event')
                pass

            elif event_type == 'push':
                # TODO: Check here immediately if repo and ref is in config, and only enqueue if yes?
                log.info(f'Enqueued job for delivery with id {delivery_id}')
                __job_queue.put(DeploymentJob(delivery_id, payload))
                return web.Response(status=200, text=f'Delivery accepted and job enqueued.')

        else:
            log.warning(f'Invalid signature from {req.remote}')

    except json.decoder.JSONDecodeError as ex:
        log.error(f'JSON decode error: {ex.msg} from {req.remote}')
        return web.Response(status=400)

    except KeyError as ex:
        log.error(f'Key error: {ex} from {req.remote}')
        return web.Response(status=400)


def worker():
    log.info('Worker started')

    while True:
        log.debug('Worker waiting for jobs')
        job = __job_queue.get()
        log.debug(f'Worker got jobs {job}')

        run_deployment_job(job)

        log.debug('Worker done with job')


worker_thread = threading.Thread(target=worker)
worker_thread.start()

app = web.Application()
app.add_routes([web.post('/github-webhook', github_webhook_handle)])

web.run_app(app)
