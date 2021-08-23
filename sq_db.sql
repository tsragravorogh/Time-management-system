CREATE TABLE IF NOT EXISTS usermenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS adminmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS startmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
email text NOT NULL,
psw text NOT NULL,
username text NOT NULL,
usertype integer DEFAULT 1,
avatar BLOB DEFAULT NULL,
time NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
id integer PRIMARY KEY AUTOINCREMENT,
task text NOT NULL,
importance integer NOT NULL,
status text NOT NULL,
user_id integer NOT NULL,
description text NOT NULL,
time NUMERIC NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id)
);