from quart import Quart, request
import ujson as json
import os

app = Quart(__name__,
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')

if not os.path.exists("log_tokens.json"):
    with open("log_tokens.json", "w") as file:
        json.dump({}, file)

@app.route('/logtoken/<token>')
async def logtoken(token):
    with open("log_tokens.json", "r") as file:
        fp = json.load(file)
        if fp.get(token) is None:
            return "400", 400
    return "200", 200

@app.route('/logs/', methods=["POST"])
async def get_logs():
    with open("log_tokens.json", "r") as file:
        fp = json.load(file)
        if fp[request.headers.get("token")] is None:
            return "401", 401
    response = await request.get_json()
    if len(response) == 0: return "400", 400
    logs = []
    for key in response.keys():
        logs.append(response[key])
    with open("log_tokens.json", "a") as file:
        fp = json.load(file)
        fp[request.headers.get("token")] = logs
        json.dump(fp, file)
    return "200", 200

app.run(port=8000)
