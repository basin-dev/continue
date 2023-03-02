# FastAPI Server

Run the server:

1. `cd continue/package`
2. `poetry shell`
3. Install everything else: `poetry install`
4. Make sure there is a `.env` file with the following:
   - OPENAI_API_KEY
5. Go back to `continue` directory by running the `cd ..` command
6. Run `uvicorn package.server.main:app` (with the `--reload` tag if you are developing and want automatic updates upon file saves)

Setup NGINX:

1. Follow steps [here](https://www.digitalocean.com/community/tutorials/how-to-configure-nginx-as-a-reverse-proxy-on-ubuntu-22-04)
2. Setup letsencrypt certificate:
   - `sudo apt install certbot python3-certbot-nginx`
   - `sudo certbot --nginx -d basin.dev`
