import asyncio

from pyrogram import Client

from vars import *


async def genrate_session():
    while True:
        phone_number = input("Enter your phone number with the country code ")
        if not phone_number.startswith("+"):
            print("Enter your phone number with country code\n\n")
        else:
            try:
                int(phone_number[1:])
                break
            except:
                print("Phone number should be integer\n\n")

    client = Client(
        name="Hellbot",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    )
    await client.connect()

    code = await client.send_code(phone_number)
    ask_otp = input("Give me OTP ")
    otp = ask_otp.replace(" ", "")

    await client.sign_in(phone_number, code.phone_code_hash, otp)

    session_string = await client.export_session_string()
    try:
        await client.send_message("me", f"Your session string is\n`{session_string}`")
        print("Session string is sent in your saved message you can copy from their")
    except:
        print(
            "Failed to send string session to saved message you can still copy it from here")
    await client.disconnect()
    print(f"Here is your session string\n{session_string}")
    return


asyncio.run(genrate_session())
