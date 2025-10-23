import time
import json
import sys
from pymongo import MongoClient

# --- Configuration ---
EVE_JSON_FILE = '/var/log/suricata/eve.json'
MONGO_URI = 'mongodb://localhost:27017/' # Connects to our local database
DB_NAME = 'ids_dashboard'
COLLECTION_NAME = 'alerts'

def follow(thefile):
    """Generator function to tail a file like 'tail -f'."""
    try:
        thefile.seek(0, 2)  # Go to the end of the file
        while True:
            line = thefile.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly if no new line
                continue
            yield line
    except KeyboardInterrupt:
        print("\nStopping logger...")
        sys.exit()
    except Exception as e:
        print(f"Error while tailing file: {e}")
        sys.exit(1)


def connect_to_mongo():
    """Connects to MongoDB."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        # Test connection
        client.server_info()
        print("Successfully connected to MongoDB.")
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Please make sure MongoDB is running! (sudo systemctl start mongodb)")
        sys.exit(1)

# --- Main function ---
if __name__ == "__main__":
    print(f"Starting IDS Alert Logger.")
    print(f"Watching file: {EVE_JSON_FILE}")

    collection = connect_to_mongo()

    try:
        with open(EVE_JSON_FILE, 'r') as logfile:
            loglines = follow(logfile)
            print("Waiting for new alerts...")
            for line in loglines:
                try:
                    event = json.loads(line)

                    # Only process alert events
                    if event.get('event_type') == 'alert':

                        # Insert the entire alert object into MongoDB
                        collection.insert_one(event)

                        # Print a confirmation to the terminal
                        print(f"ALERT Logged: {event['alert']['signature']}")

                except json.JSONDecodeError:
                    pass  # Ignore malformed lines
                except Exception as e:
                    print(f"Error processing line: {e}")

    except FileNotFoundError:
        print(f"ERROR: Log file not found at {EVE_JSON_FILE}")
        print("Is Suricata running?")
    except KeyboardInterrupt:
        print("\nStopping logger script.")
        client.close() # Ensure client is closed on exit
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if 'client' in locals() and client: # Check if client exists before closing
             client.close()
