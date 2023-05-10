def init(App):
    app = App.app

    @app.route('/logtoken/<token>')
    async def logtoken(token):

        if token is None:
            return "400", 400
        if not App.check_expiry('log', token):
            return "400", 400

        return "200", 200
