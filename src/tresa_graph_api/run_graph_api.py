"""
This script is used to get user data from Microsoft Entra ID using Microsoft Graph API.

The user data is printed to the console in the following format:
"User ID, Display Name, Email, Member Of, Roles"

Usage: `python run_graph_api.py`
You will be prompted to open a browser and authenticate using your Admin credentials.
"""


from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
import asyncio


credentials = DeviceCodeCredential()
scopes = ['https://graph.microsoft.com/.default']

client = GraphServiceClient(credentials=credentials, scopes=scopes)


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


async def main():
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


data = asyncio.run(main())
