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
    parser.add_argument('--target-file', default=pathlib.Path(os.getenv('HOME')).joinpath('.kube/config'), help='File to add contents of file to')
    parser.add_argument('--user-name', required=True)
    parser.add_argument('--cluster-name', required=True)

    args = parser.parse_args()

    with open(f"{args.target_file}", 'r') as f:
        target_kubeconfig = yaml.safe_load(f)

    with open(f"{args.kubeconfig}", 'r') as f:
        source_kubeconfig = yaml.safe_load(f)

    if args.context_name in [context["name"] for context in target_kubeconfig["contexts"]]:
        print(f"context named {args.context_name} already present, use a different name")
        sys.exit(1)

    if args.cluster_name is not None:
        if args.cluster_name not in [cluster["name"] for cluster in target_kubeconfig["clusters"]]:
            source_kubeconfig["clusters"][0]["name"] = args.cluster_name
        else:
            print(f"cluster named {args.cluster_name} already present, use a different name")
            sys.exit(1)
    target_kubeconfig["clusters"] += source_kubeconfig["clusters"]

    if args.user_name is not None:
        if args.user_name not in [user["name"] for user in target_kubeconfig["users"]]:
            source_kubeconfig["users"][0]["name"] = args.user_name
        else:
            print(f"user named {args.user_name} already present, use a different name")
            sys.exit(1)
    target_kubeconfig["users"] += source_kubeconfig["users"]

    new_context = {
        "context": {
            "cluster": f"{args.cluster_name}",
            "user": f"{args.user_name}",
        },
        "name": f"{args.context_name}",
    }

    target_kubeconfig["contexts"].append(new_context)

    with open(f"{args.target_file}", 'w+') as f:
        yaml.dump(target_kubeconfig, f)

if __name__ == "__main__":
    sys.exit(main())

