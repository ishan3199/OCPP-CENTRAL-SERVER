from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/')
async def get_handler(request):
    return web.Response(text='get /\n')


@routes.post('/post')
async def post_handler(request):
    return web.Response(text='post /post\n')


@routes.put('/put')
async def put_handler(request):
    return web.Response(text='put /put\n')


app = web.Application()
app.add_routes(routes)
web.run_app(app)