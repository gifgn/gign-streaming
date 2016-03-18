#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Multi site streaming
"""

YOUTUBE_URL = "rtmp://a.rtmp.youtube.com/live2"
TWITCH_URL = "rtmp://twitch.com"
DASH_URL = "rtmp://localhost/dash"

SOURCE_URL = "rtmp://localhost/stream"

processes = []

import sys, subprocess, signal, MySQLdb

class Database():
    """Object contenant la connexion à une base SQL"""

    def __init__(self, db_name):
        try:
            self.db_sql = MySQLdb.connect('localhost', 'username', 'password', db_name)
            print("Connexion à la base %s établie" % db_name)

        except MySQLdb.Error as error:
            print("Erreur %d: %s" % (error.args[0], error.args[1]))
            sys.exit(1)

        self.cursor = self.db_sql.cursor(MySQLdb.cursors.DictCursor)

    def query(self, secret):
        """Exécution d'une query"""
        self.cursor.execute(" SELECT pseudo FROM users WHERE secret = %s", (secret,))
        rows = self.cursor.fetchall()
        return rows

    def execute(self, statement):
        """Exécution d'un statement"""
        cursor = self.db_sql.cursor()
        try:
            cursor.execute(statement)
        except MySQLdb.Error as error:
            print("Erreur %d: %s" % (error.args[0], error.args[1]))
        finally:
            print("Number of rows updated:", cursor.rowcount)



def parse_name(name):
    """Parse the name to get the destination streams"""

    destinations = name.split(",")
    streams = [] 

    for destination in destinations:
        if len(destination) < 2:
            continue

        streams.append(destination)

    return streams 

def get_username(secret):
    """Get the username from the secret"""
    
    db = Database('gign')
    user = db.query(secret)

    if len(user) == 1:
        return user[0]['pseudo']

    return 'th3o.smith' 

def get_url(stream):
    """Get the url to send to from the stream"""

    prefix = stream[0:2]

    if prefix == "d:":
        username = get_username(stream[2:])
        if username is None:
            return None
        return DASH_URL + "/" + username 
    elif prefix == "t:":
        return TWITCH_URL + "/" + stream[2:]
    elif prefix == "y:":
        return YOUTUBE_URL + "/" + stream[2:]

def spawn(destination, source):
    """Spawn a ffmpeg to redirect the flow"""

    print("Spawning " + destination)
    args = ["avconv", "-i", source, "-codec", "copy", "-f", "flv", destination]
    p = subprocess.Popen(args)

    return p

    

def main():
    """Entry Point"""

    name = ""

    if len(sys.argv) > 1:
        name = sys.argv[1]

    streams = parse_name(name) 
    source = SOURCE_URL + "/" + name

    for s in streams:
        dest = get_url(s)
        if dest is None:
            continue
        processes.append(spawn(dest, source))

    for p in processes:
        p.wait()

def signal_term_handler(signal, frame):
    print('got SIGTERM')
    for p in processes:
        p.kill()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_term_handler)
    main()
