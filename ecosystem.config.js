module.exports = {
  apps: [
    {
      name: "mentora-backend",
      script: "run.py",
      interpreter: "/www/wwwroot/api-mentora.allfilldev.com/venv/bin/python",
      args: "serve",
      env: {
        APP_ENV: "production",
      },
    },
  ],
};
