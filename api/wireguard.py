import requests, subprocess, base64, time, json, sys

from wireguard_docker import WireguardDocker

class Wireguard:

    _headers = {"Content-Type": "application/json"}


    def __init__(self, config):
        self.config = config
        data = None
        filename = "/settings/wireguard.json"
        
        # Load existing or create new wireguard.json 
        try:
            with open(filename) as f:
                data = json.load(f)
        except Exception as e:
            print(e)
            print("creating new wireguard config file...")
            wg_json = {
                    "wireguard_name":"wireguard",
                    "wireguard_version":"latest",
                    "patp":"",
                    "cap_add":["NET_ADMIN","SYS_MODULE"],
                    "volumes":["/lib/modules:/lib/modules"],
                    "sysctls":
                    {
                        "net.ipv4.conf.all.src_valid_mark":1
                    }
            }   
            with open(filename,'w') as f :
                json.dump(wg_json, f, indent=4)
                data = wg_json

        # Load wireguard docker
        self.wg_docker = WireguardDocker(data)
        if(self.wg_docker.is_running()):
            self.wg_docker.stop()


    def start(self):
        self.wg_docker.start()

    def stop(self):
        self.wg_docker.stop()

    def register_device(self, reg_code, url):
        # /v1/register
        update_data = {
            "reg_code" : f"{reg_code}",
            "pubkey":self.config['pubkey']
        }
        headers = {"Content-Type": "application/json"}

        response = None
        try:
            response = requests.post(f'{url}/register',json=update_data,headers=headers).json()
        except Exception as e:
            print(f"register device {e}")
            return None

        return(response['lease'])

    def register_service(self, subdomain, service_type, url):
        # /v1/create
        update_data = {
            "subdomain" : f"{subdomain}",
            "pubkey":self.config['pubkey'],
            "svc_type": service_type
        }
        headers = {"Content-Type": "application/json"}

        response = None
        try:
            response = requests.post(f'{url}/create',json=update_data,headers=headers).json()
        except Exception as e:
            print(e)
            return None
        
        # wait for it to be created
        while response['status'] == 'creating':
            try:
                response = requests.get(
                        f'{url}/retrieve?pubkey={update_data["pubkey"]}',
                        headers=headers).json()
            except Exception as e:
                print(e)
            print("Waiting for endpoint to be created")
            if(response['status'] == 'creating'):
                time.sleep(60)

        return response['status']
        
    def delete_service(self, subdomain, service_type, url):
        # /v1/delete
        update_data = {
            "subdomain" : f"{subdomain}",
            "pubkey":self.config['pubkey'],
            "svc_type": service_type
        }
        headers = {"Content-Type": "application/json"}

        response = None
        try:
            response = requests.post(f'{url}/delete',json=update_data,headers=headers).json()
        except Exception as e:
            print(e)
            return None

        print(response, file=sys.stderr)
        
    def cancel_subscription(self, reg_key, url):
        # /v1/stripe/cancel
        headers = {"Content-Type": "application/json"}
        data = {'reg_code': reg_key}
        response = None

        try:
            response = requests.post(f'{url}/stripe/cancel',json=data,headers=headers).json()
            if response['error'] == 0:
                return 200
            print(response, file=sys.stderr)
            return 400

        except Exception as e:
            print(f'err: {e}', file=sys.stderr)
            return 400

    def get_status(self,url):
        headers = {"Content-Type": "application/json"}
        response = None

        try:
            response = requests.get(
                    f'{url}/retrieve?pubkey={self.config["pubkey"]}',
                    headers=headers).json()
        except Exception as e:
            print(e)

        count =0
        while ((response['conf'] == None) and (count > 6)):
            try:
                response = requests.get(
                        f'{url}/retrieve?pubkey={self.config["pubkey"]}',
                        headers=headers).json()
            except Exception as e:
                print(e)
            count = count +1

        try:
            self.wg_config = base64.b64decode(response['conf']).decode('utf-8')

            self.wg_config = self.wg_config.replace('privkey', self.config['privkey'])
            # Setup and start the local wg client
            self.wg_docker.addConfig(self.wg_config)
        except Exception as e:
            print(response)
            print(f"get Status {e}")
            return None

        return response
 

    def setupWireguard(self, patp):
        # Setup the wireguard server
        response = self.check_wireguard();
        if response['error']==1:
            self.wg_config = self.create_wireguard(patp).decode('utf-8')
        else:
            print(response)
            self.wg_config = base64.b64decode(response['conf']).decode('utf-8')

        self.wg_config = self.wg_config.replace('privkey', self.config['privkey'])
        # Setup and start the local wg client
        self.wg_docker.addConfig(self.wg_config)

    def is_running(self):
        return self.wg_docker.is_running()

