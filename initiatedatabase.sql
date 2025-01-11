CREATE TABLE IF NOT EXISTS customers (
    customer_id         int unsigned NOT NULL auto_increment,
    name                varchar(100) NOT NULL,
    phone_number        varchar(20) NOT NULL,
    email               varchar(100) NOT NULL,
    address             varchar(255) NOT NULL,
    PRIMARY KEY         (customer_id)
);

CREATE TABLE IF NOT EXISTS items (
    item_id             int unsigned NOT NULL auto_increment,
    category            varchar(100) NOT NULL,
    item_name           varchar(100) NOT NULL,
    manufacturer        varchar(100) NOT NULL,
    description         text NOT NULL,
    stock               int unsigned NOT NULL,
    price               int unsigned NOT NULL,
    PRIMARY KEY         (item_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id            int unsigned NOT NULL auto_increment,
    datetime_ordered    datetime NOT NULL,
    customer_id         int unsigned NOT NULL,
    completed           boolean NOT NULL,
    PRIMARY KEY         (order_id),
    FOREIGN KEY         (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS ordered_items (
    ordered_items_id    int unsigned NOT NULL auto_increment,
    order_id            int unsigned NOT NULL,
    item_id             int unsigned NOT NULL,
    quantity            int unsigned NOT NULL,
    PRIMARY KEY         (ordered_items_id),
    FOREIGN KEY         (order_id) REFERENCES orders(order_id),
    FOREIGN KEY         (item_id) REFERENCES items(item_id)
);

CREATE TABLE IF NOT EXISTS cart (
    customer_id         int unsigned NOT NULL,
    item_id             int unsigned NOT NULL,
    amount              int unsigned NOT NULL,
    PRIMARY KEY         (customer_id, item_id),
    FOREIGN KEY         (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY         (item_id) REFERENCES items(item_id)
);


DELIMITER //
CREATE FUNCTION create_order(p_customer_id INT)
	RETURNS INT
BEGIN
	DECLARE counter INT UNSIGNED;
	
	-- Check if cart is empty
	SELECT COUNT(*) INTO counter
	FROM cart c
	WHERE c.customer_id = p_customer_id;
	IF counter = 0 THEN
		RETURN 0;
	END IF;
	
	-- Check if the cart contains more items than available
	SELECT COUNT(*) INTO counter
	FROM cart c
	LEFT JOIN items i ON c.item_id = i.item_id
	WHERE c.customer_id = p_customer_id AND i.stock < c.amount;
	IF counter > 0 THEN
		RETURN -1;
	END IF;
	
	-- Create an order
	INSERT INTO orders (datetime_ordered, customer_id, completed)
	VALUES (NOW(), p_customer_id, FALSE);
	
	-- Copy the items from the cart to ordered items table and delete all items from the cart
	INSERT INTO ordered_items (order_id, item_id, quantity)
	SELECT LAST_INSERT_ID(), item_id, amount
	FROM cart c
	WHERE c.customer_id = p_customer_id;

	DELETE FROM cart c
	WHERE c.customer_id = p_customer_id;
	RETURN 1;
END //

DELIMITER ;


DELIMITER //
CREATE TRIGGER send_item
AFTER INSERT ON ordered_items
FOR EACH ROW
BEGIN
	UPDATE items
	SET stock = stock - NEW.quantity
	WHERE item_id = NEW.item_id;
END //
DELIMITER ;




INSERT INTO items (category, item_name, manufacturer, description, stock, price)
VALUES
('Electronics', 'Smart TV', 'Samsung', 'A 4K smart TV with Wi-Fi connectivity and voice control.', 20, 800),
('Electronics', 'Wireless Headphones', 'Sony', 'Noise-cancelling wireless headphones with long battery life.', 18, 250),
('Electronics', 'Gaming Console', 'PlayStation', 'High-performance gaming console with 4K resolution and controller.', 10, 400),
('Electronics', 'Smartwatch', 'Apple', 'A sleek smartwatch with fitness tracking and notification features.', 15, 300),
('Electronics', 'Portable Charger', 'Anker', 'A compact portable charger with high-capacity battery and fast charging.', 25, 50),
('Fashion', 'Leather Jacket', 'Gucci', 'A stylish leather jacket with adjustable cuffs and hem.', 15, 500),
('Fashion', 'Denim Jeans', 'Levi\'s', 'Classic straight-leg denim jeans with adjustable waist.', 40, 80),
('Fashion', 'Sunglasses', 'Ray-Ban', 'Stylish sunglasses with polarized lenses and adjustable frame.', 28, 100),
('Home Decor', 'Wooden Coffee Table', 'IKEA', 'A minimalist wooden coffee table with storage space.', 30, 200),
('Home Decor', 'LED Desk Lamp', 'Philips', 'Energy-efficient LED desk lamp with adjustable arm.', 22, 50),
('Sports', 'Basketball Shoes', 'Nike', 'High-performance basketball shoes with cushioning and support.', 25, 120),
('Sports', 'Tennis Racket', 'Wilson', 'High-quality tennis racket with graphite frame and strings.', 12, 150),
('Sports', 'Football', 'Adidas', 'A high-quality football with durable leather and precise stitching.', 18, 80),
('Sports', 'Running Shoes', 'Asics', 'Lightweight running shoes with cushioning and support.', 20, 100),
('Sports', 'Golf Clubs', 'Callaway', 'A set of high-quality golf clubs with durable materials and precise craftsmanship.', 10, 500),
('Books', 'Fiction Novel', 'Penguin', 'A bestselling fiction novel with engaging storyline and characters.', 25, 20),
('Books', 'Self-Help Book', 'HarperCollins', 'A motivational self-help book with practical advice and inspiring stories.', 18, 30),
('Books', 'Cookbook', 'Random House', 'A comprehensive cookbook with delicious recipes and beautiful photography.', 20, 40),
('Books', 'Biography', 'Simon & Schuster', 'A fascinating biography of a historical figure with engaging narrative and insightful analysis.', 15, 35);


INSERT INTO customers (name, phone_number, email, address)
VALUES
('Gustav Eriksson', '081523', 'gustavvasa@trekronor.se', 'Tre Kronor, Stockholm, Sverige'),
('Nils Dacke', '04701542', 'nilsdacke@kronobergsslott.se', 'Kronobergs slott, Småland, Sverige'),
('Sven Svensson', '0701236789', 'svensvensson@hotmail.se', 'Svengatan 1, Svensryd 12345, Sverige');
