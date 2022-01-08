#!/usr/bin/env python

import os
import sys
import yaml
import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description="Script used to combine kubeconfig files")
    parser.add_argument('kubeconfig')
    parser.add_argument('--context-name', dest='context_name', required=True)
    parser.add_argument('--target-file', default=pathlib.Path(os.getenv('HOME')).joinpath('.kube/config'), help='File to add contents of file to', dest='target_file')
    parser.add_argument('--user-name')
    parser.add_argument('--cluster-name')

    args = parser.parse_args()
    kubeconfig = args.kubeconfig
    target_file = args.target_file

    with open(f"{target_file}", 'r') as f:
        target_kubeconfig = yaml.safe_load(f)

    with open(f"{kubeconfig}", 'r') as f:
        source_kubeconfig = yaml.safe_load(f)

    if args.cluster_name is not None:
        #TODO: handle multiple source clusters
        print(args.cluster_name)
        source_kubeconfig["clusters"][0]["name"] = args.cluster_name
    target_kubeconfig["clusters"] += source_kubeconfig["clusters"]

    if args.user_name is not None:
        #TODO: handle multiple source users
        source_kubeconfig["users"][0]["name"] = args.user_name
    target_kubeconfig["users"] += source_kubeconfig["users"]

    new_context = {
        "context": {
            "cluster": f"{source_kubeconfig['clusters'][0]['name']}",
            "user": f"{source_kubeconfig['users'][0]['name']}",
        },
        "name": f"{args.context_name}",
    }

    target_kubeconfig["contexts"].append(new_context)

    with open(f"{target_file}", 'w+') as f:
        yaml.dump(target_kubeconfig, f)

if __name__ == "__main__":
    sys.exit(main())

