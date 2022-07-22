from getpass import getpass
from typing import List

import dotenv

dotenv.load_dotenv(".env")

import argparse
import asyncio
import os
import shutil

from pydantic import EmailError, EmailStr
from pymongo.errors import CollectionInvalid
from pymongo.results import InsertOneResult

from app import collections, settings
from app.core import aggregations, passwd, timezone
from app.core.constants import (
    MONGO_COLLECTIONS,
    MONGO_TEXT_INDEXES,
    PAYMENT_IMAGES_PATH,
    STATIC_PAYMENT_IMAGES_PATH,
    STATIC_ROOT,
)
from app.core.enums import PaymentGateway
from app.core.setup import install_payment_gateway, unregister_payment_methods
from app.extensions.mongodb import getpay_db


async def drop_collections(force: bool = False):
    if not force:
        y = input("Please confirm to reset the database (y/n): ")
        if y.lower() != "y":
            print("Aborting...")
            exit(1)

    print("Dropping collections...")
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


async def create_admin(
    username: str = None, password: str = None, skip_confirmation: bool = False
):
    try:
        if not skip_confirmation:
            answer = input("Do you want to create an admin user? (y/n): ").lower()
            if not answer.startswith("y"):
                print("Skip...")
                return

        print("Creating admin...")
        username = username or input("Username: ")
        password = password or getpass("Password: ")
        if username and password:
            await create_user(username, password)
        else:
            print("Username and password are required to create an admin user. Skip...")
            return
    except KeyboardInterrupt:
        print("\nAborting...")


async def create_payment_gateways():
    if (
        settings.IPAYMU_API_KEY
        and settings.IPAYMU_CALLBACK_URL
        and settings.IPAYMU_URL
        and settings.IPAYMU_VIRTUAL_ACCOUNT
    ):
        await install_payment_gateway(PaymentGateway.ipaymu)

    if (
        settings.XENDIT_API_KEY
        and settings.XENDIT_QRCODE_CALLBACK_URL
        and settings.XENDIT_SECRET_KEY
    ):
        await install_payment_gateway(PaymentGateway.xendit)

    if (
        settings.DUITKU_API_KEY
        and settings.DUITKU_MERCHANT_CODE
        and settings.DUITKU_URL
    ):
        await install_payment_gateway(PaymentGateway.duitku)


async def init_payment_method_images():
    os.makedirs(STATIC_PAYMENT_IMAGES_PATH, exist_ok=True)

    def _check(key: str, items: List[str]):
        key = key.lower()
        for v in items:
            if v.lower() in key:
                return True
        return False

    print("* Initializing payment method images...")
    cursor = collections.payment_channel.find({"img": {"$type": 10}})
    for channel in await cursor.to_list(None):
        logo = None
        name: str = channel["name"].lower()
        if "cimb" in name:
            logo = "cimb.png"
        elif _check(name, ("BNI", "Bank Negara Indonesia")):
            logo = "bni.png"
        elif _check(name, ("BAG", "Bank Artha Graha")):
            logo = "bag.jpg"
        elif "mandiri" in name:
            logo = "mandiri.png"
        elif "muamalat" in name:
            logo = "muamalat.jpg"
        elif _check(name, ("BRI", "Bank Rakyat Indonesia")):
            logo = "bri.png"
        elif _check(name, ("BCA", "Bank Central Asia")):
            logo = "bca.png"
        elif _check(name, ("Link Aja", "LINKAJA")):
            logo = "linkaja.png"
        elif "indomaret" in name:
            logo = "indomaret.png"
        elif "alfamart" in name:
            logo = "alfamart.png"
        elif "permata" in name:
            logo = "permata.png"
        elif "sahabat sampoerna" in name:
            logo = "banksampoerna.png"
        elif _check(name, ("BSI", "Bank Syariah Indonesia")):
            logo = "bsi.png"
        elif _check(name, ("BJB", "Bank Jabar Banten")):
            logo = "bjb.png"
        elif "ovo" in name:
            logo = "ovo.png"
        elif "dana" in name:
            logo = "dana.png"
        elif _check(name, ("sakuku", "saku ku")):
            logo = "sakuku.png"
        elif "shopee" in name:
            logo = "shopeepay.png"
        elif "qris" in name:
            logo = "qris.svg"
        elif "maybank" in name:
            logo = "maybank.svg"
        elif _check(name, ("BNC", "Neo")):
            logo = "neo.png"
        elif "atm bersama" in name:
            logo = "atm_bersama.svg"

        if logo is None:
            print("! No logo found for:", name)
        else:
            src_img = PAYMENT_IMAGES_PATH / logo
            if src_img.is_file():
                dst_img = STATIC_PAYMENT_IMAGES_PATH / logo
                if not dst_img.is_file():
                    shutil.copyfile(src_img, dst_img)

                img_path = f"/{STATIC_ROOT}/payments/{logo}"
                media_obj = await collections.media.find_one({"file": img_path})
                if not media_obj:
                    print(" + Creating media file:", name, logo)
                    await collections.media.insert_one(
                        {
                            "file": img_path,
                            "date_created": timezone.now(),
                            "date_updated": None,
                        }
                    )
                else:
                    print(" ! Media file already exists:", name, logo)

                await collections.payment_channel.update_one(
                    {"_id": channel["_id"]}, {"$set": {"img": img_path}}
                )
            else:
                print(f"! Payment method image for {name} not found")

    await remove_duplicate_images()


async def remove_duplicate_images():
    aggr = aggregations.find_duplicate_data("$file")
    async for doc in collections.media.aggregate(aggr):
        print("Removing duplicate media file:", doc["id"])
        await collections.media.delete_one({"_id": doc["id"]})


async def main():
    parser = argparse.ArgumentParser()
    try:
        subparsers = parser.add_subparsers(dest="command")
        subparsers.add_parser("init", help="Data initialization")
        create_user_parser = subparsers.add_parser("create_user", help="Create user")
        create_user_parser.add_argument(
            "-u", "--username", dest="username", help="Username (Email)"
        )
        create_user_parser.add_argument(
            "-p", "--password", dest="password", help="Password (min 8 character)"
        )
        create_user_parser.add_argument(
            "-y", "--yes", dest="yes", action="store_true", help="Skip confirmation"
        )
        drop_collection_parser = subparsers.add_parser(
            "drop_collection", help="Drop collection"
        )
        drop_collection_parser.add_argument(
            "-f", "--force", dest="force", action="store_true", default=False
        )
        args = parser.parse_args()
        cmd = args.command
        if cmd == "init":
            await create_collections()
            await create_payment_gateways()
            await init_payment_method_images()
            await unregister_payment_methods()
        elif cmd == "create_user":
            await create_admin(args.username, args.password, args.yes)
        elif cmd == "drop_collection":
            await drop_collections(args.force)
        else:
            parser.print_help()

    except argparse.ArgumentError as e:
        parser.error(e)


if __name__ == "__main__":
    asyncio.run(main())
