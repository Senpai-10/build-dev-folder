#!/bin/env python

import click
import requests
import os
from math import floor, log
from click import style as cs
from click import echo as ce


@click.group()
def cli():
    ...


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
    show_default=True,
    default="awesome-config,nvim-config,dotfiles",
    required=False,
)
def build(username: str, destination: str, skip: str):
    username = username or click.prompt("Username")
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

    click.secho("-----------------------------------", fg="black")
    ce(f"{cs('Username', bold=True)}: {cs(username, fg='bright_yellow')}")
    ce(f"{cs('Destination', bold=True)}: {cs(destination, fg='bright_yellow')}")
    ce(f"{cs('Skip list', bold=True)}: {cs(skip_list, fg='bright_yellow')}")
    ce(f"{cs('Total count', bold=True)}: {cs(total_count, fg='bright_yellow')}")
    ce(f"{cs('Items', bold=True)}: {cs(len(items), fg='bright_yellow')}")
    ce(
        f"{cs('Incomplete results', bold=True)}: {cs(incomplete_results, fg='bright_yellow')}"
    )
    click.secho("-----------------------------------\n", fg="black")

    click.confirm("Do you want to continue?", abort=True)

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

        ce(
            "{} ({}) [{}/{}]".format(
                cs(repo.name, fg="bright_yellow"),
                cs(repo.default_branch, fg="bright_magenta"),
                cs(index + 1, fg="bright_yellow"),
                cs(len(items), fg="bright_yellow"),
            )
        )
        ce(
            "{}: {}".format(
                cs("Description", bold=True), cs(repo.description, fg="bright_yellow")
            )
        )
        ce(
            "{}: {}".format(
                cs("Language", bold=True), cs(repo.language, fg="bright_yellow")
            )
        )
        ce(
            "{}: {}".format(
                cs("Size", bold=True), cs(format_bytes(repo.size), fg="bright_yellow")
            )
        )
        ce("{}: {}".format(cs("Fork?", bold=True), cs(repo.fork, fg="bright_yellow")))
        ce("{}: {}".format(cs("Private?", bold=True), cs(repo.private, fg="bright_yellow")))
        ce("--------------- Cloning Repo ---------------")
        os.system(f"git clone {repo.html_url} {dest}")
        click.secho("-----------------------------------\n", fg="black")

        exit(0)


if __name__ == "__main__":
    cli()
