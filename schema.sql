DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);


DROP TABLE IF EXISTS musicals;

CREATE TABLE musicals
(
    musical_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image TEXT NOT NULL,
    price REAL NOT NULL,
    language TEXT NOT NULL,
    date TEXT NOT NULL,
    number INTEGER NOT NULL

);

INSERT INTO musicals (name, image, price, language, date, number)
VALUES
    ('Future life', 'future.jpg', 134, 'English, French, Germany', '2023-03-16', 100),
    ('Friendship', 'friendship.jpg', 234, 'English, French, Germany', '2023-10-02', 100),
    ('Old town in rome', 'rome.jpg', 310, 'English, French, Germany', '2023-10-12', 100),
    ('Sunset', 'sunset.jpg', 125, 'English, French, Germany', '2024-11-02', 100),
    ('Cat', 'cat.jpg', 134, 'English, French, Germany', '2023-07-09', 100),
    ('Tower in the west', 'tower.jpg', 150, 'English, French, Germany', '2023-05-02', 100),
    ('Seven', 'car.jpg', 210, 'English, French, Germany', '2023-12-17', 100),
    ('The short story', 'vanity.jpg', 175, 'English, French, Germany', '2024-02-12', 100);


DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    r_user TEXT NOT NULL,
    title TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    date_reviewed DATETIME NOT NULL
);


DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    o_id INTEGER PRIMARY KEY AUTOINCREMENT,
    o_name TEXT NOT NULL,
    o_price REAL NOT NULL,
    o_quantity NOT NULL
);

DROP TABLE IF EXISTS contacts;

CREATE TABLE contacts
(
    c_user TEXT NOT NULL,
    c_email TEXT NOT NULL,
    c_topic TEXT NOT NULL,
    c_message TEXT NOT NULL
);



