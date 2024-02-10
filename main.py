#!/bin/env python

import os
import requests
import click
from math import floor, log


def format_bytes(size: int):
    power = 0 if size <= 0 else floor(log(size, 1024))
    return (
        f"{round(size / 1024 ** power, 2)} {['B', 'KB', 'MB', 'GB', 'TB'][int(power)]}"
    )


class Repo:
    id: int
    name: str
    private: bool
    html_url: str
    description: str
    fork: bool
    created_at: str
    updated_at: str
    pushed_at: str
    size: int
    language: str
    default_branch: str

    def __init__(self, item: dict):
        self.id = item["id"]
        self.name = item["name"]
        self.private = item["private"]
        self.html_url = item["html_url"]
        self.description = item["description"]
        self.fork = item["fork"]
        self.created_at = item["created_at"]
        self.updated_at = item["updated_at"]
        self.pushed_at = item["pushed_at"]
        self.size = item["size"]
        self.language = item["language"]
        self.default_branch = item["default_branch"]


def get_token():
    git_credentials = os.path.expanduser("~/.git-credentials")

    if os.path.exists(git_credentials):
        with open(git_credentials, "r") as f:
            line = f.readline()
            token = line.split("@")[0].split(":")[2]

            return token
    else:
        token = input("Token: ")

        return token


def main():
    ...


@click.group()
def cli():
    ...


@cli.command()
@click.option("-u", "--username", type=str, required=False)
@click.option(
    "-d",
    "--destination",
    type=str,
    default="Development",
    show_default=True,
    required=False,
)
@click.option(
    "-s",
    "--skip",
    type=str,
    default="awesome-config,nvim-config",
    required=False,
)
def build(username: str, destination: str, skip: str):
    username = username or input("Username: ")
    skip_list = skip.split(",")

    token = get_token()

    req = requests.get(
        f"https://api.github.com/search/repositories?q=user:{username}&per_page=1000",
        headers={"Authorization": f"token {token}"},
    )

    data = req.json()

    total_count = data["total_count"]
    incomplete_results = data["incomplete_results"]
    items = data["items"]

    click.echo(f"Username: {username}")
    click.echo(f"Destination: {destination}")
    click.echo(f"Skip list: {skip_list}")
    click.echo(f"Total count: {total_count}")
    click.echo(f"Items: {len(items)}")
    click.echo(f"Incomplete results: {incomplete_results}")
    click.echo("-----------------------------------\n")

    continue_confirm = input("Do you want to continue? (Y/n): ") or "y"

    if continue_confirm.lower() != "y":
        exit(0)

    if os.path.exists(destination):
        print(f"Directory '{destination}' already exists!")
        overwirte_confirm = input("overwrite? (Y/n): ") or "y"

        if overwirte_confirm.lower() != "y":
            exit(0)
        else:
            print(f"Removing old dest directory ({destination}).....")
            os.rmdir(destination)

    print(f"Creating dest directory ({destination}).....")
    os.mkdir(destination)

    for index, item in enumerate(items):
        repo = Repo(item)
        dest = os.path.join(destination, repo.name)

        if repo.name in skip_list:
            continue

        print(f"{repo.name} ({repo.default_branch}) [{index + 1}/{len(items)}]")
        print(f"Description: {repo.description}")
        print(f"Destination: {os.getcwd()}/{dest}")
        print(f"Language: {repo.language}")
        print(f"Size: {format_bytes(repo.size)}")
        print(f"Fork?: {repo.fork}")
        print(f"Private?: {repo.private}")
        os.system(f"git clone {repo.html_url} {dest}")
        print("-" * 15, "\n")


@cli.command()
def fetch():
    click.echo("Hello World!")


if __name__ == "__main__":
    cli()
