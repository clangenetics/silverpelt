import os
from quart import request, Quart
import quart_uploads

def init(App: Quart):
    app = App.app
    

    uploadset = quart_uploads.UploadSet('save', ('zip',), lambda app: "temp")
    quart_uploads.configure_uploads(app, upload_sets=uploadset)

    @app.route('/save/', methods=["POST"])
    async def save():  # pylint: disable=too-many-branches
        token = request.headers.get("token")
        if token is None:
            return "401", 401
        if not App.check_expiry('save', token):
            return "401", 401

        _token = token
        token = App.get_token('save', token)

        if not App.rest.is_alive:
            App.rest.start()

        files = await request.files

        if 'file' not in files:
            return "400", 400
        
        await uploadset.save(files['file'], folder=str(token['requester']), name="save.zip")

        channel = await App.rest.fetch_channel(token["channel"])

        await channel.send(
            content=f"<@{token['requester']}>'s saves are ready!",
            attachments=[f"temp/{token['requester']}/save.zip"],
            user_mentions=[token['requester']]
        )

        os.remove(f"temp/{token['requester']}/save.zip")

        App.remove_token('save', _token)
        return "200", 200
