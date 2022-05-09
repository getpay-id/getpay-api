import dotenv

dotenv.load_dotenv(".env")

import asyncio
import os

from pydantic import EmailError, EmailStr
from pymongo.errors import CollectionInvalid
from pymongo.results import InsertOneResult

from app import collections, settings
from app.core import passwd, timezone
from app.core.constants import MONGO_COLLECTIONS, MONGO_TEXT_INDEXES
from app.core.enums import PaymentGateway
from app.core.setup import install_payment_gateway
from app.extensions.mongodb import getpay_db


async def drop_collections(force: bool = False):
    if "GETPAY_RESET" in os.environ or force:
        y = input("Please confirm to reset the database (y/n): ")
        if y.lower() != "y":
            print("Aborting...")
            exit(1)

        for coll in MONGO_COLLECTIONS:
            try:
                await getpay_db[coll].drop_indexes()
                await getpay_db.drop_collection(coll)
            except CollectionInvalid:
                pass


async def create_collections():
    print("Creating collections...")
    for coll in MONGO_COLLECTIONS:
        try:
            await getpay_db.create_collection(coll)
        except CollectionInvalid:
            pass

        text_indexes = MONGO_TEXT_INDEXES.get(coll, [])
        indexes = []
        for idx in text_indexes:
            indexes.append((idx, "text"))

        if indexes:
            await getpay_db[coll].create_index(indexes)


async def create_user(username: str, password: str) -> str:
    try:
        EmailStr.validate(username)
    except EmailError:
        print(f"Invalid username: {username} (should be an email address)")
        exit(1)

    if len(password) < 8:
        print("Password should be at least 8 characters")
        exit(1)

    usr_obj = await collections.users.find_one({"username": username})
    if not usr_obj:
        usr: InsertOneResult = await collections.users.insert_one(
            {
                "username": username,
                "password": passwd.encrypt(password),
                "date_created": timezone.now(),
                "date_updated": None,
            }
        )
        print(f"User {username!r} created")
        uid = str(usr.inserted_id)
    else:
        uid = str(usr_obj["_id"])
        print(f"User {username} already exists with id: {uid}")

    return uid


async def create_admin():
    print("Creating admin...")
    username = settings.ADMIN_USERNAME
    password = settings.ADMIN_PASSWORD
    if username and password:
        await create_user(username, password)
    else:
        print(
            "Admin user not found. Please set ADMIN_USERNAME and ADMIN_PASSWORD in .env"
        )
        exit(1)


async def create_payment_gateways():
    await install_payment_gateway(PaymentGateway.ipaymu)
    await install_payment_gateway(PaymentGateway.xendit)
    await install_payment_gateway(PaymentGateway.duitku)


async def main():
    await drop_collections()
    await create_collections()
    await create_admin()
    await create_payment_gateways()


if __name__ == "__main__":
    asyncio.run(main())
