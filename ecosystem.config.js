require("dotenv").config();
module.exports = {
    apps: [{
        name: "silverpelt-"+process.env.ENVIRONMENT,
        script: "./main.py",
        interpreter: "python3",
        log_file: "silverpelt.log",
        env_production: {
            PREFIX: "$",
            NODE_ENV: "production"
        },
        env_development: {
            PREFIX: "~",
            NODE_ENV: "development"
        }
    }],

    deploy: {
        production: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/prod",
            repo: "git@github.com:clangen-devs/silverpelt.git",
            path: "/home/luna/servers/silverpelt",
            "post-deploy": "npm install && pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env production"
        },
        development: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/master",
            repo: "git@github.com:clangen-devs/silverpelt.git",
            path: "/home/luna/servers/silverpelt-dev",
            "post-deploy": "npm install && pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env development"
        }
    }
}