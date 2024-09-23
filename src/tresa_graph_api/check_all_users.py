"""
This script is used to get user data from Microsoft Entra ID using Microsoft Graph API.

The user data is printed to the console in the following format:
"User ID, Display Name, Email, Member Of, Roles"

Usage: `python check_all_users.py`
You will be prompted to open a browser and authenticate using your Admin credentials.
"""

import argparse
import asyncio
import sys

from azure.identity import DeviceCodeCredential  # type: ignore[import-not-found]
from msgraph import GraphServiceClient  # type: ignore[import-not-found]

credentials = DeviceCodeCredential()
scopes = ["https://graph.microsoft.com/.default"]

client = GraphServiceClient(credentials=credentials, scopes=scopes)


def cli(args=None):
    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Get user data from Microsoft Entra ID using Microsoft Graph API."
    )
    subparsers = parser.add_subparsers(dest="command")

    user_parser = subparsers.add_parser("user", help="Get user data.")
    user_parser.add_argument("--id", type=str, help="The user ID to get data for.")
    user_parser.add_argument("--name", type=str, help="The user name to get data for.")
    user_parser.add_argument(
        "--email", type=str, help="The user email to get data for."
    )
    user_parser.add_argument(
        "--admins", action="store_true", help="Get data for all admins."
    )
    user_parser.add_argument(
        "--unassigned", action="store_true", help="Get data for all unassigned users."
    )

    subparsers.add_parser("group", help="Get group data.")

    args = parser.parse_args(args)
    asyncio.run(main(args))


async def get_users():
    users = await client.users.get()
    return users.value


async def get_user_roles(user_id):
    roles = await client.users.by_user_id(user_id).member_of.get()
    roles = roles.value
    return [role.display_name for role in roles]


async def get_groups():
    groups = await client.groups.get()
    groups = groups.value
    group_data = {}
    for group in groups:
        group_name = group.display_name
        members = await client.groups.by_group_id(group.id).members.get()
        group_data[group_name] = [member.id for member in members.value]

    return group_data


async def main(args):
    users = await get_users()
    groups = await get_groups()

    if args.command == "user":
        if args.id:
            fetched_users = [user for user in users if user.id == args.id]
        elif args.name:
            fetched_users = [user for user in users if args.name in user.display_name]
        elif args.email:
            fetched_users = [user for user in users if user.mail == args.email]
        elif args.admins or args.unassigned:
            fetched_users = users

        print("User ID, Display Name, Email, Member of, Is Global Admin")
        print("--------------------------------------------------------")

        if fetched_users and not (args.admins or args.unassigned):
            for user in fetched_users:
                member_of = []
                roles = await get_user_roles(user.id)
                is_admin = "Global Administrator" in roles
                for group_name, members in groups.items():
                    if user.id in members:
                        member_of.append(group_name)
                print(
                    user.id,
                    ",",
                    user.display_name,
                    ",",
                    user.mail,
                    ",",
                    member_of,
                    ",",
                    is_admin,
                )
                print("\n")
        elif fetched_users and args.admins:
            for user in fetched_users:
                roles = await get_user_roles(user.id)
                is_admin = "Global Administrator" in roles
                if is_admin:
                    member_of = []
                    for group_name, members in groups.items():
                        if user.id in members:
                            member_of.append(group_name)
                    print(
                        user.id,
                        ",",
                        user.display_name,
                        ",",
                        user.mail,
                        ",",
                        member_of,
                        ",",
                        is_admin,
                    )
                    print("\n")
        elif fetched_users and args.unassigned:
            for user in fetched_users:
                is_member = False
                for _, members in groups.items():
                    if user.id in members:
                        is_member = True
                        break
                if not is_member:
                    roles = await get_user_roles(user.id)
                    is_admin = "Global Administrator" in roles
                    print(
                        user.id,
                        ",",
                        user.display_name,
                        ",",
                        user.mail,
                        ",",
                        [],
                        ",",
                        is_admin,
                    )
                    print("\n")
        else:
            print("No users found for the given criteria.")

    elif args.command == "group":
        print("Requested group data")


if __name__ == "__main__":
    cli()
