from responder import API, Request, Response
import schema
from models import database, create_tables, Kigo, Image, Haiku
from peewee import SQL, fn
from collections import Counter
from base64 import urlsafe_b64encode
from uuid import uuid1

api = API(cors=True, cors_params={
    'allow_origins': ['*'],
    'allow_methods': ['*'],
    'allow_headers': ['*'],
})


@api.route('/haiku')
class HaikuResource:
    async def on_get(self, req: Request, resp: Response):
        """
        response
        [
          {
            "first": "柿くへば",
            "second": "鐘が鳴るなり",
            "third": "法隆寺",
            "kigo": "柿",
            "season": "fall"
          }
        ]
        """
        resp.media = [{'first': h.first,
                       'second': h.second,
                       'third': h.third,
                       'kigo': h.kigo.kigo,
                       'season': h.kigo.season.name.lower()}
                      for h in Haiku.select()]

    async def on_post(self, req: Request, resp: Response):
        """
        request
        {
            first: "柿食えば",
            second: "鐘が鳴るなり",
            third: "法隆寺"
        }
        response
        {
          "images": [
            "/static/6qqV9MTuEemXsrj2sRfcWw.png",
            "/static/L2oLJMUTEem_8bj2sRfcWw.png"
          ],
          "season": "fall"
        }
        """

        haiku = schema.Haiku().load(await req.media())

        kigo = Kigo.select().where(
            (fn.Instr(haiku['first'], Kigo.kigo) > 0) |
            (fn.Instr(haiku['second'], Kigo.kigo) > 0) |
            (fn.Instr(haiku['third'], Kigo.kigo) > 0)
        ).first()

        Haiku.create(first=haiku['first'], second=haiku['second'],
                     third=haiku['third'], kigo=kigo).save()

        resp.media = {
            'images': [req.api.static_url(i.image + '.png') for i in kigo.images],
            'season': kigo.season.name.lower()
        }


@api.route('/upload')
async def upload_kigo(req: Request, resp: Response):
    @api.background.task
    def process_data(data, kigo):
        image_id = urlsafe_b64encode(uuid1().bytes).rstrip(b'=').decode('ascii')
        with open(f"static/{image_id}.png", 'wb') as f:
            f.write(data['image']['content'])

        kigo = Kigo.get(kigo=kigo)
        Image.create(image=image_id, kigo=kigo).save()

    process_data(await req.media(format='files'), req.params['kigo'])

    resp.media = {'success': 'ok'}


@api.on_event('startup')
async def start_db_connection():
    create_tables()


@api.on_event('shutdown')
def close_db_connection():
    database.close()


if __name__ == '__main__':
    api.run()
