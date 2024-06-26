"""An example of a simple HTTP server."""
import json
import mimetypes
import pickle
import socket
from os import listdir
from os.path import isdir, isfile, join
from urllib.parse import unquote_plus

# Pickle file for storing data
PICKLE_DB = "db.pkl"

# Directory containing www data
WWW_DATA = "www-data"

# Header template for a successful HTTP request
HEADER_RESPONSE_200 = """HTTP/1.1 200 OK\r
content-type: %s\r
content-length: %d\r
connection: Close\r
\r
"""

# Represents a table row that holds user data
TABLE_ROW = """
<tr>
    <td>%d</td>
    <td>%s</td>
    <td>%s</td>
</tr>
"""

# Template for a 301 (Moved Permanently) error
RESPONSE_301 = """HTTP/1.1 301 Moved Permanently\r
location: %s\r
\r
"""

# Template for a 404 (Not found) error
RESPONSE_404 = """HTTP/1.1 404 Not found\r
content-type: text/html\r
connection: Close\r
\r
<!doctype html>
<h1>404 Page not found</h1>
<p>Page cannot be found.</p>
"""

DIRECTORY_LISTING = """<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<title>Directory listing: %s</title>

<h1>Contents of %s:</h1>

<ul>
%s
</ul> 
"""

FILE_TEMPLATE = "  <li><a href='%s'>%s</li>"


def save_to_db(first, last):
    """Create a new user with given first and last name and store it into
    file-based database.

    For instance, save_to_db("Mick", "Jagger"), will create a new user
    "Mick Jagger" and also assign him a unique number.

    Do not modify this method."""

    existing = read_from_db()
    existing.append({
        "number": 1 if len(existing) == 0 else existing[-1]["number"] + 1,
        "first": first,
        "last": last
    })
    with open(PICKLE_DB, "wb") as handle:
        pickle.dump(existing, handle)


def read_from_db(criteria=None):
    """Read entries from the file-based DB subject to provided criteria

    Use this method to get users from the DB. The criteria parameters should
    either be omitted (returns all users) or be a dict that represents a query
    filter. For instance:
    - read_from_db({"number": 1}) will return a list of users with number 1
    - read_from_db({"first": "bob"}) will return a list of users whose first
    name is "bob".

    Do not modify this method."""
    if criteria is None:
        criteria = {}
    else:
        # remove empty criteria values
        for key in ("number", "first", "last"):
            if key in criteria and criteria[key] == "":
                del criteria[key]

        # cast number to int
        if "number" in criteria:
            criteria["number"] = int(criteria["number"])

    try:
        with open(PICKLE_DB, "rb") as handle:
            data = pickle.load(handle)

        filtered = []
        for entry in data:
            predicate = True

            for key, val in criteria.items():
                if val != entry[key]:
                    predicate = False

            if predicate:
                filtered.append(entry)

        return filtered
    except (IOError, EOFError):
        return []

def create_directory_listing(uri):
    contents = []
    contents.append(FILE_TEMPLATE % ("..", ".."))
    for item in listdir(WWW_DATA + uri):
        contents.append(FILE_TEMPLATE % (item, item))
    contents.sort()
    return (DIRECTORY_LISTING % (uri, uri, '\n'.join(contents))).encode("utf-8")

def process_request(connection, address):
    """Process an incoming socket request.

    :param connection is a socket of the client
    :param address is a 2-tuple (address(str), port(int)) of the client
    """

    # Read and parse the request line
    client = connection.makefile("wrb")
    try:
        line = client.readline().decode("utf-8").strip()
        print(line)
        method, uri, version = line.split(" ")
        assert method == "GET" or method == "POST", f"Unsupported method: {method}"
        assert uri.startswith("/"), f"Unsupported URI: {uri}"
        assert version == "HTTP/1.1", f"Unsupported version: {version}"
    except (ValueError, AssertionError) as e:
        print(f"Bad request: {e}")
        return

    # Read and parse headers
    try:
        headers = dict()
        while True:
            line = client.readline().decode("utf-8").strip()
            print(line)
            if not line:
                break
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    except ValueError as e:
        print(f"Bad request headers: {e}")
        return

    # Read and parse the body of the request (if applicable)
    try:
        body = None
        if "content-length" in headers:
            body = client.read(int(headers["content-length"]))
            body = json.loads(body)
            print(body)
    except ValueError as e:
        print(f"Bad request body: {e}")
        return

    # create the response
    try:
        if uri[-1] == "/" and isdir(WWW_DATA + uri):
            if isfile(WWW_DATA + uri + "index.html"):
                with open(WWW_DATA + uri + "index.html", "rb") as file:
                    body = file.read()
                header = HEADER_RESPONSE_200 % (
                    mimetypes.guess_type(uri + "index.html")[0],
                    len(body)
                )
                client.write(header.encode("utf-8"))
                client.write(body)
                client.close()
                return
                
            body = create_directory_listing(uri)
            header = HEADER_RESPONSE_200 % (
                "text/html",
                len(body)
            )
            
        elif isdir(WWW_DATA + uri):
            client.write((RESPONSE_301 % (uri + "/")).encode("utf-8"))
            client.close()
            return
        
        elif isfile(WWW_DATA + uri):            
            with open(WWW_DATA + uri, "rb") as file:
                body = file.read()
            
            header = HEADER_RESPONSE_200 % (
                mimetypes.guess_type(uri)[0],
                len(body)
            )
            
        else:
            raise Exception("File not found")

    except Exception as e:
        print(f"Error: {e}")
        client.write(RESPONSE_404.encode("utf-8"))
        client.close()
        return

    # Write the response back to the socket
    client.write(header.encode("utf-8"))
    client.write(body)
    client.close()


def main(port):
    """Starts the server and waits for connections."""

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", port))
    server.listen(1)

    print("Listening on %d" % port)

    while True:
        connection, address = server.accept()
        print("[%s:%d] CONNECTED\n" % address)
        process_request(connection, address)
        connection.close()
        print("[%s:%d] DISCONNECTED" % address)


if __name__ == "__main__":
    main(8080)
