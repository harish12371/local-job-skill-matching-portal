
import getpass
import ssl
from pathlib import Path
import pymysql

HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
PORT = 4000
USERNAME = "2gyt3mJGgdzLU5K.root"

CA_FILE = (
    Path(__file__).resolve().parent.parent
    / "certs"
    / "isrgrootx1.pem"
)

print("TiDB Direct Login Test")
print("----------------------")

if not CA_FILE.is_file():
    raise FileNotFoundError(f"CA certificate missing: {CA_FILE}")

password = getpass.getpass("Enter your NEW TiDB password: ")

try:
    connection = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USERNAME,
        password=password,
        database="test",
        ssl={"ca": str(CA_FILE)},
        connect_timeout=15
    )

    print("\nSUCCESS: TiDB authentication worked!")
    print("Database connection established.")

    connection.close()

except Exception as error:
    print("\nCONNECTION FAILED")
    print("Error type:", type(error).__name__)
    print("Error:", error)

finally:
    password = None
