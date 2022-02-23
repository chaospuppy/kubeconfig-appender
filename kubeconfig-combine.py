#!/usr/bin/env python

import os
import sys
import yaml
import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description="Script used to combine kubeconfig files")
    parser.add_argument('kubeconfig', type=str)
    parser.add_argument('--context-name', type=str)
    parser.add_argument('--target-file', default=pathlib.Path(os.getenv('HOME')).joinpath('.kube/config'), help='File to add contents of file to')
    parser.add_argument('--user-name', type=str)
    parser.add_argument('--cluster-name', type=str)
    parser.add_argument('--all-name', type=str)
    parser.add_argument('--allow-overwrite', action='store_true', default=False)

    args = parser.parse_args()

    if hasattr(args, "all_name"):
      cluster_name = args.all_name
      context_name = args.all_name
      user_name = args.all_name
    else:
      cluster_name = args.cluster_name
      context_name = args.context_name
      user_name = args.user_name

    with open(f"{args.target_file}", 'r') as f:
      target_kubeconfig = yaml.safe_load(f)

    with open(f"{args.kubeconfig}", 'r') as f:
      source_kubeconfig = yaml.safe_load(f)

    if cluster_name not in [cluster["name"] for cluster in target_kubeconfig["clusters"]]:
      source_kubeconfig["clusters"][0]["name"] = cluster_name
      target_kubeconfig["clusters"] += source_kubeconfig["clusters"]
    elif args.allow_overwrite:
      source_kubeconfig["clusters"][0]["name"] = cluster_name
      for i, k in enumerate(target_kubeconfig["clusters"]):
        if target_kubeconfig["clusters"][i]["name"] == cluster_name:
          print(i)
          target_kubeconfig["clusters"][i] = source_kubeconfig["clusters"][0]
    else:
        print(f"cluster named {cluster_name} already present, use a different name")
        sys.exit(1)

    if user_name not in [user["name"] for user in target_kubeconfig["users"]]:
      source_kubeconfig["users"][0]["name"] = user_name
      target_kubeconfig["users"] += source_kubeconfig["users"]
    elif args.allow_overwrite:
      source_kubeconfig["users"][0]["name"] = user_name
      for i, k in enumerate(target_kubeconfig["users"]):
        if target_kubeconfig["users"][i]["name"] == user_name:
          target_kubeconfig["users"][i] = source_kubeconfig["users"][0]
    else:
      print(f"user named {user_name} already present, use a different name")
      sys.exit(1)

    new_context = {
        "context": {
            "cluster": f"{cluster_name}",
            "user": f"{user_name}",
        },
        "name": f"{context_name}",
    }

    if context_name not in [context["name"] for context in target_kubeconfig["contexts"]]:
      target_kubeconfig["contexts"].append(new_context)
      # If context is already present and allow override is false, fail
    elif args.allow_overwrite:
      target_kubeconfig[context_name] = new_context
      for i, k in enumerate(target_kubeconfig["contexts"]):
        if target_kubeconfig["contexts"][i]["name"] == context_name:
          target_kubeconfig["contexts"][i] = new_context
    else:
      print(f"context named {context_name} already present, use a different name")
      sys.exit(1)

    with open(f"{args.target_file}", 'w+') as f:
        yaml.dump(target_kubeconfig, f)

if __name__ == "__main__":
    sys.exit(main())

