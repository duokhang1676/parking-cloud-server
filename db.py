from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def get_db():
    """
    Kết nối đến MongoDB và trả về đối tượng database.
    """
    uri = "mongodb+srv://duongkhang1676:01678192452aA@db-cluster.95rw7.mongodb.net/?retryWrites=true&w=majority&appName=db-cluster"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client["Smart_Parking"]
    return db