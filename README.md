# unit-test-experiments

Run the server:
0. SSH into the AWS EC2 machine: ubuntu@ec2-35-174-135-225.compute-1.amazonaws.com
1. `cd unit-test-experiments`
2. Make sure the server is not already running with `screen -r`
3. `sudo apt-get update`
4. `sudo apt install python3.10-venv`
5. `source env/bin/activate`
6. Because `torch` normally needs 2GiB+ of memory for installation, use `pip install torch==1.13.0+cpu --no-cache-dir -f https://download.pytorch.org/whl/torch_stable.html` and make sure you don't separately install it in the `requirements.txt`.
7. Install everything else: `pip install -r requirements.txt --no-cache-dir`
8. If you run into a memory error, do `pip cache purge` and run the above command again repeatedly until everything is installed.
9. Run `screen` command to make sure the server will stay up after you disconnect
10. `uvicorn server:app --reload`
11. If you are seeing any errors that seem dependency related, you can try uninstall and reinstalling the problematic packages.
12. Make sure there is a `.env` file with the following:
    - OPENAI_API_KEY

Setup NGINX:
1. Follow steps [here](https://www.digitalocean.com/community/tutorials/how-to-configure-nginx-as-a-reverse-proxy-on-ubuntu-22-04)
2. Setup letsencrypt certificate:
    - `sudo apt install certbot python3-certbot-nginx`
    - `sudo certbot --nginx -d basin.dev`