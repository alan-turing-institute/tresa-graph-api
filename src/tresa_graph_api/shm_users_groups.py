import argparse
import asyncio
import sys

from azure.identity import (  # type: ignore[import-not-found]
    InteractiveBrowserCredential,
)
from msgraph import GraphServiceClient  # type: ignore[import-not-found]

credentials = InteractiveBrowserCredential()
scopes = ["https://graph.microsoft.com/.default"]

client = GraphServiceClient(credentials=credentials, scopes=scopes)


def cli(args=None):
    if not args:
        args = sys.argv[1:]  # takes the arguments from the command line

    parser = argparse.ArgumentParser(
        description="""
        Get user and group data from Microsoft Entra ID using the Microsoft Graph API.
        You will be prompted to open a browser and authenticate using your Admin
        credentials. The results of the query will be printed to the terminal.
        """
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
    user_parser.add_argument(
        "--all", action="store_true", help="Get data for all users."
    )

    group_parser = subparsers.add_parser("group", help="Get group data.")
    group_parser.add_argument(
        "--name", type=str, help="The group name to get data for."
    )
    group_parser.add_argument(
        "--all", action="store_true", help="Get data for all groups."
    )

    args = parser.parse_args(args)
    asyncio.run(main(args))


async def get_users():
    """Fetches information about all users in the organization."""
    users = await client.users.get()
    return users.value


async def get_user_roles(user_id):
    """Fetches the roles of a user in the organization."""
    roles = await client.users.by_user_id(user_id).member_of.get()
    roles = roles.value
    return [role.display_name for role in roles]


async def get_groups():
    """Fetches information about all groups in the organization."""
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
            fetched_users = [
                user for user in users if args.name.lower() in user.display_name.lower()
            ]
        elif args.email:
            fetched_users = []
            for user in users:
                try:
                    if user.mail.lower() == args.email.lower():
                        fetched_users.append(user)
                except AttributeError:
                    # Some users do not have an email address
                    continue
        elif args.admins or args.unassigned or args.all:
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
        if args.name:
            group_names = [
                group_name
                for group_name in groups
                if args.name.lower() in group_name.lower()
            ]
            if group_names:
                for group_name in group_names:
                    members = groups[group_name]
                    print(f"Group: {group_name}")
                    print("--------------------")
                    print("User ID, Display Name, Email")
                    print("----------------------------")
                    for member_id in members:
                        try:
                            member = next(
                                user for user in users if user.id == member_id
                            )
                        except StopIteration:
                            continue
                        print(member.id, ",", member.display_name, ",", member.mail)
                        print("\n")
                    print("\n")
            else:
                print("No group found for the given criteria.")
        elif args.all:
            for group_name, members in groups.items():
                print(f"Group: {group_name}")
                print("--------------------")
                print("User ID, Display Name, Email")
                print("----------------------------")
                for member_id in members:
                    try:
                        member = next(user for user in users if user.id == member_id)
                    except StopIteration:
                        continue
                    print(member.id, ",", member.display_name, ",", member.mail)
                    print("\n")
                print("\n")


if __name__ == "__main__":
    cli()
