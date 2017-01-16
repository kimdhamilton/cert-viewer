#!/usr/bin/env
'''
Loads certificates to the mongodb used so that they are available from the cert-viewer flask app when using gridfs.

Note that cert_store_path option is used to find the certificates.
'''
import glob
import gridfs
import configargparse
from pymongo import MongoClient
import os


v1_cert_transaction_ids = {
    '56aa4c9bf3a6a0125aaf24bf': '48f64ff1517554dac3496e9da0a28ca0ae492682b0898e38a4e17e7f90ee1295',
    '56aa4c9bf3a6a0125aaf24c7': '1e031ea6895a4f00a3cbb1b68650d1ee0f9bb555bf6490d404ede56a7a630afa'
}

def load_gridfs(config):
    mongodb_uri = config.mongodb_uri
    client = MongoClient(host=mongodb_uri)
    conn = client[mongodb_uri[mongodb_uri.rfind('/') + 1:len(mongodb_uri)]]

    fs = gridfs.GridFS(conn)

    cert_glob = os.path.join(config.cert_store_path, '*.json')
    json_files = glob.glob(cert_glob)

    for f in json_files:
        with open(f) as infile:
            filename = os.path.basename(f)
            content = infile.read()
            fs.put(content, filename=filename, encoding='utf-8')
            out = fs.find_one({'filename': filename})
            print('filename: ' + filename)
            print(out.read())


def load_txids(config):
    mongodb_uri = config.mongodb_uri
    client = MongoClient(host=mongodb_uri)

    for k, v in v1_cert_transaction_ids.items():
        client['test']['certificates'].insert_one({'uid': k, 'txid': v})


def get_config():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    p = configargparse.getArgumentParser(default_config_files=[os.path.join(base_dir, 'conf.ini')]) 
    p.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
    p.add_argument('-m', '--mongodb_uri', type=str, default='mongodb://127.0.0.1:27017/test', help='the mongo DB to load the certificates')
    p.add_argument('-s', '--cert_store_path', type=str, default='.', help='the path where the certificates can be found')
    args, _ = p.parse_known_args()

    return args



if __name__ == "__main__":
    conf = get_config()
    load_gridfs(conf)
    load_txids(conf)
