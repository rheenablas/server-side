DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    name TEXT NOT NULL
);

DROP TABLE IF EXISTS menu;

CREATE TABLE menu
(
    food_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    price REAL NOT NULL,
    description TEXT, 
    allergens TEXT

);

INSERT INTO menu (name, price, description, allergens)
VALUES
    ('Silvanas', 20, 'Meringue coated in buttercream, coated in crumbs', 'Eggs, Nuts'),
    ('Sansrival', 55, 'Meringue cake coated in buttercream, topped with pistacios/cashew', 'Eggs, Nuts'),
    ('Strawberry Cake', 50, '', 'Dairy, Eggs' ),
    ('Longganisa', 16, 'Sweet garlic sausage', 'Pork'),
    ('Oreo Cheesecake', 35, '', 'Dairy' ),
    ('Seafood Pasta', 20, '', 'Crustacean' ),
    ('Pad Thai', 20, '' , 'Eggs, Peanuts'),
    ('Chicken Wings', 20, '', ' ' ),
    ('Butterscotch', 20, 'Irresistably delicious cake.', 'Nuts' ),
    ('Nachos', 15, 'Perfect snack while watching movies! ','Dairy'),
    ('Salad', 10, '', 'Nuts' ),
    ('Sushi', 10, '', 'Fish' ),
    ('Ube Cake', 35, '', 'Dairy, Eggs'),
    ('Ice Cream', 10, 'Homemade dairy ice cream', 'Dairy' ),
    ('Veggie Wrap', 10, '3 pcs of vegetable wrapped in  egg crepe dipped in garlic peanut sauce',' ' ),
    ('Black Forest Cake', 55, '', 'Dairy, Eggs' ),
    ('Muffins', 10, '', 'Dairy, Eggs, Nuts' ),
    ('Food for the gods', 10, 'Feelin fancy? Try this! ', 'Nuts, Eggs' ),
    ('Crinkles', 10, 'Perfect holiday snack!' ,'Eggs'),
    ('Lengua', 20, 'Ox-tongue in creamy sauce with chorizo and mushrooms', 'Milk' ),
    ('Cordon Bleu', 20, 'Chicken-cheese-ham rolled in bread crumbs with white garlic sauce.', 'Dairy, Egg' ),
    ('Tempura Platter', 20, 'Deep fried shrimp/eggplant/sweeet potato/fish/calamari dipped in tempura batter', 'Crustaceans, Fish' ),
    ('Crispy Pork Belly', 20, 'Oven-cooked pork belly', 'Pork' ),
    ('Chopsuey', 20, 'Stir-fry vegetables with oyster sauce', '' );

DROP TABLE IF EXISTS varieties;

CREATE TABLE varieties
(
    name VARCHAR,
    var TEXT 
);

INSERT INTO varieties
VALUES
    ('Sansrival', 'Pistachio'),
    ('Sansrival', 'Cashew'),
    ('Sansrival', 'Ube'),
    ('Sansrival', 'Cashew'),
    ('Silvanas', 'Assorted'),
    ('Silvanas', 'Pistacio'),
    ('Silvanas', 'Cashew'),
    ('Silvanas', 'Chocolate'),
    ('Silvanas', 'Cookies n Creme'),
    ('Silvanas', 'Ginger nut'),
    ('Chicken Wings', 'Plain'),
    ('Chicken Wings', 'Spicy'),
    ('Chicken Wings', 'Buffalo'),
    ('Chicken Wings', 'Honey Sriracha'),
    ('Muffins', 'Assorted'),
    ('Muffins', 'Strawberry'),
    ('Muffins', 'Pistachio'),
    ('Muffins', 'Blueberry'),
    ('Ice Cream', 'Ube'),
    ('Ice Cream', 'Pistachio'),
    ('Ice Cream', 'Strawberry');


DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR NOT NULL,
    n_food VARCHAR NOT NULL,
    review TEXT NOT NULL
);

Insert into reviews (user_id, n_food, review)
Values ('rna', 'Chopsuey', 'Yummy!! My favorite!'), 
    ('rna', 'Lengua','The meat is so tender, I did not know I was eating tongue!'),
    ('qwerty', 'Silvanas', 'It was so tempting!! I had to shot myself with the epi-pen first before eating! WORTH IT!!!');


DROP TABLE IF EXISTS requests;

CREATE TABLE requests
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR NOT NULL,
    food NOT NULL,
    status TEXT,
    date DATE NOT NULL
);

Insert into requests (user_id, food, status, date)
Values ('rna', 'chicken pot pie', 'READ', '2021-03-21'), ('qwert', 'teriyaki chicken', 'UNREAD', '2021-03-20');


DROP TABLE IF EXISTS order_info;

CREATE TABLE order_info
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR NOT NULL,
    date_of_order DATETIME,
    date_del DATE NOT NULL,
    time_del TIME NOT NULL,
    address TEXT NOT NULL,
    info TEXT,
    status TEXT, 
    total REAL NOT NULL
);

DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    oi_id INTEGER,
    food_id INTEGER,
    qty INTEGER
);

Insert into orders 
Values (1, 4, 1), (1, 3, 2), (2, 5, 1), (2, 2, 1), (2, 1, 1), (3, 1, 2);

INSERT into order_info (user_id, date_of_order, date_del, time_del, info, status, total, address)
values ('rna', '2021-03-18', '2021-03-20', '13:00', '', 'DONE', 31, '1 abrgr'),
        ('qwerty', '2021-03-18', '2021-03-31','13:00', '','PENDING', 90, '3 bdbfbd'),
        ('qwerty', '2021-03-22', '2021-03-31','13:00', '','PENDING', 40, '3 bdbfbd');

