import httpx
import asyncio
import time
import os
from dotenv import load_dotenv
load_dotenv()
import traceback
import subprocess


CONN_FAILED = 502
INTERNAL_ERR = 500

# cmd can take values "start" and "stop"
def toggle_db(cmd = "stop"):
    if (cmd != "stop" and cmd != "start"):
        print(f"Invalid cmd {cmd}")
        return
    try:
        subprocess.run(["docker", "compose", cmd, "db"], check = True)
        time.sleep(3)
    except subprocess.CalledProcessError:
        print(f"Unable to {cmd} the database. Try again later...")
    except Exception as e:
        print(f"Something happened while trying to {cmd} the database. Please check before continuing operations.")
        print(e)
    
async def call_app(msg, col_change=False):
    res = ""
    client_name = f"Testing_validation"

    test_data = {
        "usr_cl_name": client_name,
        "usr_level": "LOG",
        "usr_msg": msg
    }
    if col_change:
        test_data = {
            "cl_name": client_name,
            "usr_level": "LOG",
            "usr_msg": msg
        }   
    async with httpx.AsyncClient() as client:
        try:
            server_url = os.getenv("SERVER_URL")
            # Send a request to the server and wait for response.
            res = await client.post(f"{server_url}/ingest", json = test_data)
        except httpx.ConnectError:
            print("Connection failed: Please ensure that the server is running.")
            raise
        except Exception as e:
            msg = f"Error Type: {type(e).__name__} - {e}"
            print(msg)
            raise
    return res
async def db_up_test():
    # 1. Test when db up
    try:
        res = await call_app("Test validation:Happy path!")
        print(res.content)
        assert(res.status_code == 200) 
    except Exception as e:
        # not supposed to get any error
        print(traceback.print_exc())
        print("Something wrong happened")
        return
    print(">>>> Happy path validation done.")

async def db_down_test():
    toggle_db("stop")
    try:
        res = await call_app("Validation test msg:Db down path")
        assert(res.status_code == 500)
    except Exception as e:
        assert(type(e).__name__ == "ConnectError" )
    toggle_db("start")
    print(">>>> Db down path validation done!")

async def db_no_env_test():
    org_db_url = os.getenv("DATABASE_URL_DOCKER")
    os.environ["DATABASE_URL_DOCKER"] = "" 
    try:
        await call_app("Validation test msg:DB no url")
    except Exception as e:
        assert(type(e).__name__ == "ConnectError")
    print(">>>> DB no env variable validtion done!")
    os.environ["DATABASE_URL_DOCKER"] = org_db_url

async def db_invalid_creds():
    org_db_url = os.getenv("DATABASE_URL_DOCKER")
    wrong_db_url =os.getenv("DATABASE_WRONG_URL")
    os.environ["DATABASE_URL_DOCKER"] = wrong_db_url
    try:
        res = await call_app("Validation test msg:DB invalid database url")
    except Exception as e:
        assert(type(e).__name__ == "ConnectError")
        #print("Invalid credentials. Check DB username and password")
    print(">>>> DB invalid credentials validtion done!")
    os.environ["DATABASE_URL_DOCKER"] = org_db_url

async def inval_usr_input():
    try:
        res = await call_app(1)
        assert(res.status_code == 422)
    except Exception as e:
        print(traceback.print_exc())
    print(">>>> Invalid user input validation done!")

async def inval_db_column():
    try:
        res = await call_app("Validation test msg:Invalid db column", True)
        assert(res.status_code == 422)
    except Exception as e:
        print(traceback.print_exc())
    print(">>>> Invalid db column validation done!") 

async def cleanup():
    async with httpx.AsyncClient() as client:
        try:
            server_url = os.getenv("SERVER_URL")
            secret_token = os.getenv("TEST_CLEANUP_TOKEN")
            headers = {"in-token":secret_token}
            res = await client.post(f"{server_url}/app/cleanup", headers = headers)
            if res.status_code == 200:
                print("Database cleared of test logs successfully!")
            return res.status_code
        except httpx.ConnectError:
            print("Connection failed: Please ensure that the server is running.")
            return CONN_FAILED
        except Exception as e:
                msg = f"Error Type: {type(e).__name__} - {e}"
                print(msg, "Couldn't erase DB test logs")
                return INTERNAL_ERR

async def testing_path():

    #Happy Path!
    await db_up_test()
    
    # Test when the database is down
    await db_down_test()
    
    # Test when no env variable for db
    await db_no_env_test()

    # Test when the db credentials are wrong.
    await db_invalid_creds()

    # Test Validation error
    await inval_usr_input()

    # Test change in columns/wrong columns for db addition.
    await inval_db_column()

    await cleanup()
    return
if __name__ == "__main__":
    asyncio.run(testing_path())
