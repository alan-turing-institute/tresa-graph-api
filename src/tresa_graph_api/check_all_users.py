"""
This script is used to get user data from Microsoft Entra ID using Microsoft Graph API.

The user data is printed to the console in the following format:
"User ID, Display Name, Email, Member Of, Roles"

Usage: `python check_all_users.py`
You will be prompted to open a browser and authenticate using your Admin credentials.
"""


from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
import asyncio
import argparse
import sys


credentials = DeviceCodeCredential()
scopes = ['https://graph.microsoft.com/.default']

client = GraphServiceClient(credentials=credentials, scopes=scopes)


def cli(args=None):

    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Get user data from Microsoft Entra ID using Microsoft Graph API.")
    subparsers = parser.add_subparsers(dest="command")

    user_parser = subparsers.add_parser("user", help="Get user data.")
    user_parser.add_argument("--id", type=str, help="The user ID to get data for.")
    user_parser.add_argument("--name", type=str, help="The user name to get data for.")
    user_parser.add_argument("--email", type=str, help="The user email to get data for.")
    user_parser.add_argument("--admins", action="store_true", help="Get data for all admins.")
    user_parser.add_argument("--unassigned", action="store_true", help="Get data for all unassigned users.")

    subparsers.add_parser("group", help="Get group data.")

    args = parser.parse_args(args)
    asyncio.run(main(args))


async def get_users():
    users = await client.users.get()
    return users.value


async def get_user_roles(user_id):
    roles = await client.users.by_user_id(user_id).member_of.get()
    roles = roles.value
    roles = [role.display_name for role in roles]
    return roles


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

    print("User ID, Display Name, Email, Member Of, Roles")
    print("----------------------------------------------")
    for user in users:
        member_of = []
        roles = await get_user_roles(user.id)
        for name, members in groups.items():
            if user.id in members:
                member_of.append(name)
        print(user.id, ",", user.display_name, ",", user.mail, ",", member_of, ",", roles)


if __name__ == "__main__":
    cli()
