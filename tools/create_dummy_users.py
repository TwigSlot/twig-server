from pprint import pprint
import requests
import uuid
import json
import pathlib

THIS_FILE_DIR = pathlib.Path(__file__).parent.resolve()

# Note: Needs the admin endpoint
KRATOS_ADMIN_ENDPOINT = "http://localhost:4434"
KRATOS_ENDPOINT = "http://localhost:4433"

session = requests.Session()

IDENT_SCHM = "default"


def fetch_schemas(sess: requests.Session = session):
    resp = sess.get(f"{KRATOS_ENDPOINT}/schemas")
    resp.raise_for_status()
    return resp.json()


def create_user(username: str, password: str, first_name: str = "",
                last_name: str = "", *, sess: requests.Session = session):
    """
    Create a user with the given username and password.

    Args:
        username: The **email** of the user.
        password: The password of the user.
        first_name: The first name of the user. Blank by default
        last_name: The last name of the user. Blank by default
        sess: The session to use.
    """
    # TODO: This is hardcoded and should probably depend on the schema, but oh well.
    response = sess.post(
        f"{KRATOS_ADMIN_ENDPOINT}/admin/identities",
        json={
            "credentials": {
                "password": {
                    "config": {
                        "password": password
                    }
                }
            },
            "state": "active",
            "schema_id": IDENT_SCHM,
            "traits": {
                "email": username,
                "name": {
                    "first": first_name,
                    "last": last_name
                }
            },
            "verifiable_addresses": [
                {
                    "id": str(uuid.uuid4()),
                    "status": "verified",
                    "value": username,
                    "verified": True,
                    "via": IDENT_SCHM
                }
            ]
        },
    )
    return response


# check for IDENT_SCHM
# print(fetch_schemas()[0]["id"])
# pprint(fetch_schemas())
if __name__ == "__main__":
    with open(f"{THIS_FILE_DIR}/dev_dummy_data/users.json") as f:
        users = json.load(f)
        for user in users:
            creation_resp = create_user(**user)
            if creation_resp.status_code != 201:
                print(f"Failed to create user {user['username']}")
                print(creation_resp.text)
            else:
                print(f"Created user: {user['username']} | {user['password']}")
