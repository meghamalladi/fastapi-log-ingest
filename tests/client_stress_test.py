import httpx
import asyncio
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

TOTAL_REQUESTS = 20
TASK_LIMIT = 200

#ERRORS
SUCCESS = 200
CONN_FAILED = 502
INTERNAL_ERR = 500

async def post_log(client, t_id):
    test_data = {
        "usr_cl_name": f"Testing_client_stress{t_id}",
        "usr_level": "LOG",
        "usr_msg": f"Stress test msg {t_id}",
        "usr_cl_ts": datetime.now(timezone.utc).isoformat()
    }
    try:
        server_url = os.getenv("SERVER_URL")
        res = await client.post(f"{server_url}/ingest", json = test_data)
        # check if the http client is retrying. 
        if res.history:
            print(f"task was retried {len(res.history)} times")
            for old_res in res.history:
                print(f"Previous attempt failed with: {old_res.status_code}")
        return res.status_code
    except httpx.ConnectError:
        print("Connection failed: Please ensure that the server is running.")
        return CONN_FAILED
    except Exception as e:
            msg = f"Error Type: {type(e).__name__} - {e}"
            print(msg)
            return INTERNAL_ERR
    return -1

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
async def start_stress_test():

    print("Stress test begins..")
    start_time = time.perf_counter()

    sem = asyncio.Semaphore(TASK_LIMIT)

    async def each_task(client, t_id):
        async with sem:
            return await post_log(client, t_id)
        
    async with httpx.AsyncClient() as client:
        funcs = []
        for i in range(TOTAL_REQUESTS):
            funcs.append(each_task(client, i))
            
        res = await asyncio.gather(*funcs)
    end_time = time.perf_counter()

    duration = end_time - start_time
    res_len = len(res)

    success = res.count(SUCCESS)
    errors = res_len - success

    rps = TOTAL_REQUESTS / duration

    print(f"Total time taken ={duration} seconds")
    print(f"Average requests per second = {rps}")
    print(f"Number of successful requests = {success}")
    print(f"Number of failed requests = {errors}. Examples are as follows:")

    for i in range(res_len):
        if res[i] != 200:
            print(res[i])
    
    print("Stress test ends here...")
    
    # Cleanup all the test entries after your job is done. 
    #await cleanup()

if __name__ == "__main__":

    # Create http async client pipeline and then pool of worker threads
    asyncio.run(start_stress_test())

