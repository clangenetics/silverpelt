module.exports = {
    apps: [{
        name: "silverpelt",
        script: "./main.py",
        interpreter: "python3",
        log_file: "silverpelt.log",
        env_production: {
            PORT: "8273",
            PREFIX: "$"
        },
        env_development: {
            PORT: "8000",
            PREFIX: "~"
        }
    }],

    deploy: {
        production: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/release",
            repo: "git@github.com:clangen-devs/silverpelt.git",
            path: "/home/luna/servers/silverpelt",
            "post-deploy": "pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env production"
        },
        development: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/master",
            repo: "git@github.com:clangen-devs/silverpelt.git",
            path: "/home/luna/servers/silverpelt-dev",
            "post-deploy": "pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env development"
        }
    }
}