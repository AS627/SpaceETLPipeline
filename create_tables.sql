CREATE DATABASE IF NOT EXISTS spaceBDD;
USE spaceBDD;

CREATE TABLE IF NOT EXISTS spaceBDD.rockets (
	id varchar(256) UNIQUE NOT NULL,
	name varchar(256),
    height numeric(18,0),
	mass INT,
	diameter numeric(18,0),
    first_flight DATETIME,
    cost_per_launch INT,
    thrust_to_weight numeric(18,0),
    acceleration numeric(18,0)
);

CREATE TABLE IF NOT EXISTS spaceBDD.rocket_images (
	id INT NOT NULL ,
    rocket_id VARCHAR(256) NOT NULL,
    image_url varchar(256)
);


CREATE TABLE IF NOT EXISTS spaceBDD.launches (
	id VARCHAR(256) UNIQUE NOT NULL,
    launch_name VARCHAR(256),
    rocket_id VARCHAR(256),
    success BOOL,
    launch_date DATETIME
);

CREATE TABLE IF NOT EXISTS spaceBDD.launch_images (
	id INT NOT NULL,
    launch_id VARCHAR(256) NOT NULL,
    rocket_id VARCHAR(256),
    image_url VARCHAR(256)
);


CREATE TABLE IF NOT EXISTS spaceBDD.launchpad (
	id VARCHAR(256) NOT NULL,
    launch_id VARCHAR(256) NOT NULL,
    pad_name VARCHAR(256),
    locality VARCHAR(256),
    region VARCHAR(256),
    activity_status BOOL
);

CREATE TABLE IF NOT EXISTS spaceBDD.landpad (
	id VARCHAR(256) NOT NULL,
    launch_id VARCHAR(256) NOT NULL,
    pad_name VARCHAR(256),
    locality VARCHAR(256),
    region VARCHAR(256),
    activity_status BOOL
);

ALTER TABLE rockets
ADD PRIMARY KEY (id);

ALTER TABLE launches
ADD PRIMARY KEY (id);

ALTER TABLE launches
ADD FOREIGN KEY (rocket_id) REFERENCES rockets(id);

ALTER TABLE launch_images
ADD PRIMARY KEY (id, launch_id);

ALTER TABLE launch_images
ADD FOREIGN KEY (launch_id) REFERENCES launches(id);

ALTER TABLE rocket_images
ADD PRIMARY KEY (id, rocket_id);

ALTER TABLE rocket_images 
ADD FOREIGN KEY (rocket_id) REFERENCES rockets(id);

ALTER TABLE launchpad
ADD PRIMARY KEY (id, launch_id);

ALTER TABLE launchpad
ADD FOREIGN KEY (launch_id) REFERENCES launches(id);

ALTER TABLE landpad
ADD PRIMARY KEY (id, launch_id);

ALTER TABLE landpad
ADD FOREIGN KEY (launch_id) REFERENCES launches(id);