#!/usr/bin/python3
from Mikrotik import Mikrotik
import json
from datetime import datetime
import pathlib
import sys

if __name__ == '__main__':

    path = pathlib.Path(__file__).parent.resolve()
    with open('{}/mikrotikBgp.log'.format(path), 'a') as log_file:
        log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = " ".join(sys.argv[1:])
        # print('{} {}'.format(log_time, params), file=log_file)

    if len(sys.argv) < 6:
        print("{} <IP> <USER> <PASS> <API_PORT> <METHOD>".format(sys.argv[0]))
        sys.exit(1)

    if sys.argv[5] == 'getPeerInfo' and len(sys.argv) < 7:
        print("{} <IP> <USER> <PASS> <API_PORT> <METHOD> <PEER_NAME>".format(sys.argv[0]))
        sys.exit(1)

    ip = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    api_port = sys.argv[4]
    method = sys.argv[5]

    router = Mikrotik()
    router.connect(host=ip, username=username, password=password, port=api_port)

    if router.error:
        print("0")
        sys.exit(1)

    if method == 'getPeers':
        response = router.get_all_bgp_peers()

        if router.error or not response:
            print("")
            sys.exit(1)

        print(json.dumps(response).replace(" ", ""))

    elif method == 'getPeerInfo':
        peer_name = sys.argv[6]

        response = router.get_bgp_peer_info(peer_name,
                                            True if len(sys.argv) >= 8 and sys.argv[7] == 'advertisements' else False)
        if router.error or not response:
            sys.exit(1)

        if len(sys.argv) >= 8:
            item = sys.argv[7]
            if item in response['data']:
                item_response = response['data'][item]
                if isinstance(item_response, str):
                    item_response = item_response.replace(" ", "")
                print(response['data'][item])
            else:
                print("0")
                sys.exit(1)
        else:
            print(json.dumps(response).replace(" ", ""))

    else:
        print("Método não identificado")
