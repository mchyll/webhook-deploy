from aiohttp import web
import json
from main import verify_signature, load_config, load_secret


__config = load_config()
__secret = load_secret()


async def github_webhook_handle(req: web.Request):
    try:
        payload = await req.text()
        signature = req.headers['X-Hub-Signature']
        delivery_id = req.headers['X-GitHub-Delivery']
        event_type = req.headers['X-GitHub-Event']

        if verify_signature(payload, signature, __secret):
            if event_type == 'ping':
                # TODO: Check against config, log?
                pass
            elif event_type == 'push':
                print(f'Yee. Signature: {signature}, delivery id: {delivery_id}, payload: {payload}')
                return web.Response(status=200, text=f'Yee. Signature: {signature}, delivery id: {delivery_id}, payload: {payload}')
        else:
            # TODO: Warn log about invalid signature
            pass

    except json.decoder.JSONDecodeError as ex:
        print(f'JSON decode error: {ex.msg}')
        return web.Response(status=400)

    except KeyError as ex:
        print(f'Key error: {ex}')
        return web.Response(status=400)


app = web.Application()
app.add_routes([web.post('/github-webhook', github_webhook_handle)])

web.run_app(app)
