require("dotenv").config();
module.exports = {
    apps: [{
        name: "silverpelt-"+process.env.NODE_ENV,
        script: "./main.py",
        interpreter: "python3",
        log_file: "silverpelt.log",
        env_production: {
            PORT: "8273",
            PREFIX: "$",
            NODE_ENV: "prod"
        },
        env_development: {
            PORT: "8372",
            PREFIX: "~",
            NODE_ENV: "dev"
        },
        env_fringe: {
            PORT: "8274",
            PREFIX: "$",
            NODE_ENV: "prod"
        },
    }],

    deploy: {
        production: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/prod",
            repo: "git@github.com:clangenetics/silverpelt.git",
            path: "/home/luna/servers/silverpelt",
            "post-deploy": "npm install && pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env production"
        },
        development: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/master",
            repo: "git@github.com:clangenetics/silverpelt.git",
            path: "/home/luna/servers/silverpelt-dev",
            "post-deploy": "npm install && pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env development"
        },
        fringekit: {
            user: "luna",
            host: "silverpelt.lvna.me",
            ref: "origin/prod",
            repo: "git@github.com:clangenetics/silverpelt.git",
            path: "/home/luna/servers/fringekit",
            "post-deploy": "npm install && pip install -r requirements.txt && pm2 startOrRestart ecosystem.config.js --env fringe"
        },
    }
}