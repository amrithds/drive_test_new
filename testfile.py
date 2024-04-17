import time
import threading
def test():
        print('test')
        while True:
                print('1')
                time.sleep(3)
def test2():
        print('test2')
        while True:
                print('2')
                time.sleep(5)
# readRFIDThread = threading.Thread(target=test())
# readSTMThread = threading.Thread(target=test2())
# readRFIDThread.start()
# readSTMThread.start()

# readRFIDThread.join()
# readSTMThread.join()


import concurrent.futures
 
def worker():
    print("Worker thread running")
 
pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
 
pool.submit(test)
pool.submit(test2)
 
pool.shutdown(wait=True)
 
print("Main thread continuing to run")
