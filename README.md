# unit-test-experiments

Run the server:
1. `cd unit-test-experiments`
2. `sudo apt-get update`
3. `sudo apt install python3.10-venv`
4. `source env/bin/activate`
5. Because `torch` normally needs 2GiB+ of memory for installation, use `pip install torch==1.13.0+cpu --no-cache-dir -f https://download.pytorch.org/whl/torch_stable.html` and make sure you don't separately install it in the `requirements.txt`.
6. Install everything else: `pip install -r requirements.txt --no-cache-dir`
7. If you run into a memory error, do `pip cache purge` and run the above command again repeatedly until everything is installed.
8. `uvicorn server:app --reload`
9. If you are seeing any errors that seem dependency related, you can try uninstall and reinstalling the problematic packages.
10. Make sure there is a `.env` file with the following:
    - OPENAI_API_KEY

Setup NGINX:
1. Follow steps [here](https://www.digitalocean.com/community/tutorials/how-to-configure-nginx-as-a-reverse-proxy-on-ubuntu-22-04)
2. Setup letsencrypt certificate:
    - `sudo apt install certbot python3-certbot-nginx`
    - `sudo certbot --nginx -d basin.dev`