def init(App):
    app = App.app

    @app.route('/clantoken/<token>')
    async def clantoken(token):

        if token is None:
            return "400", 400
        if not App.check_expiry('save', token):
            return "400", 400

        return "200", 200
