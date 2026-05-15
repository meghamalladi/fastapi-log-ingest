import httpx
import asyncio
import time
import os
import sys
from sqlalchemy import create_engine, text
from database import Base
from dotenv import load_dotenv
load_dotenv()

TOTAL_REQUESTS = 500
TASK_LIMIT = 50

#ERRORS
SUCCESS = 200
CONN_FAILED = 502
INTERNAL_ERR = 500

async def post_log(client, t_id):
    test_data = {
        "usr_cl_name": f"Stress_test_client{t_id}",
        "usr_level": "LOG",
        "usr_msg": f"Stress test msg {t_id} "
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

# We need a cleanup method for cleaning up the test logs.
# I am using a sync method here to make sure that the clenaup happens
#   before we more on to the test.
def cleanup_sync():
    db_url = os.getenv("DATABASE_SYNC_URL")
    try:
        engine = create_engine(db_url)
        with engine.begin() as conn:
            result = conn.execute(text("DELETE FROM logs WHERE ldb_cl_name LIKE 'Stress_test_%'"))
            print(f"{result.rowcount} stress test records deleted from DB")
    except Exception as e:
        print(f"Could not cleanup the test logs.")
        print(f"Error Type: {type(e).__name__} - {e}")
        sys.exit(1)


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
    print(f"Number of succesful requests = {success}")
    print(f"Number of failed requests = {errors}. Examples are as follows:")

    for i in range(res_len):
        if res[i] != 200:
            print(res[i])
    
    print("Stress test ends here...")
    

if __name__ == "__main__":

    # Cleanup to start with a clean slate
    #cleanup_sync()

    # Create http async client pipeline and then pool of worker threads
    asyncio.run(start_stress_test())

    # Cleanup all the test entries. 
    cleanup_sync()
