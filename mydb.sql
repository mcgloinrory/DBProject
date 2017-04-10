CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb`;

DROP TABLE IF EXISTS `mydb`.`Portfolio` ;
DROP TABLE IF EXISTS `mydb`.`Historical_Data` ;
DROP TABLE IF EXISTS `mydb`.`Users` ;
DROP TABLE IF EXISTS `mydb`.`Stocks` ;

-- -----------------------------------------------------
-- Table `mydb`.`Users`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS `mydb`.`Users` (
  `user_id` INT NOT NULL,
  `starting_balance` INT NOT NULL,
  `current_balance` INT NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_id_UNIQUE` (`user_id` ASC))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `mydb`.`Stocks`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS `mydb`.`Stocks` (
  `stock` VARCHAR(45) NOT NULL,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`stock`),
  UNIQUE INDEX `stock_UNIQUE` (`stock` ASC))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `mydb`.`Historical_Data`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS `mydb`.`Historical_Data` (
  `date` DATE NOT NULL,
  `stock` VARCHAR(45) NOT NULL,
  `adj_closed` INT NOT NULL,
  PRIMARY KEY (`date`, `stock`),
  INDEX `fk_Historical_Data_Stocks1_idx` (`stock` ASC),
  CONSTRAINT `fk_Historical_Data_Stocks1`
    FOREIGN KEY (`stock`)
    REFERENCES `mydb`.`Stocks` (`stock`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `mydb`.`Portfolio`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS `mydb`.`Portfolio` (
  `user_id` INT NOT NULL,
  `stock` VARCHAR(45) NOT NULL,
  `p_bought_at` INT NOT NULL,
  `volume` INT NOT NULL,
  `d_bought_at` DATE NOT NULL,
  PRIMARY KEY (`user_id`, `stock`)
  INDEX `fk_Portfolio_Users_idx` (`user_id` ASC),
  INDEX `fk_Portfolio_Stocks1_idx` (`stock` ASC),
  CONSTRAINT `fk_Portfolio_Users`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`Users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Portfolio_Stocks1`
    FOREIGN KEY (`stock`)
    REFERENCES `mydb`.`Stocks` (`stock`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Insert some initial info
-- -----------------------------------------------------
INSERT INTO `mydb`.`Users` (`user_id`, `starting_balance`, `current_balance`)
	VALUES (1, 100000, 100000);
INSERT INTO `mydb`.`Stocks` (`stock`, `name`)
	VALUES ('YHOO', 'Yahoo! Inc.'),
    ('GOOGL', 'Alphabet Inc Class A'),
    ('MSFT', 'Microsoft Corporation'),
    ('TWTR', 'Twitter Inc'),
    ('AAPL', 'Apple Inc.'),
    ('INTC', 'Intel Corporation'),
    ('FB', 'Facebook, Inc.'),
    ('AMZN', 'Amazon.com, Inc.'),
    ('TSLA', 'Tesla, Inc.'),
    ('GOOG', 'Alphabet Inc Class C');
    
DROP FUNCTION IF EXISTS mydb.most_recent_data;
DELIMITER //
CREATE FUNCTION mydb.most_recent_data()
RETURNS DATE
	BEGIN
    DECLARE recent_date DATE;
    SELECT d.date 
    INTO recent_date
    FROM mydb.Historical_Data d 
    ORDER BY d.date DESC LIMIT 1;
    IF recent_date IS NULL THEN
		RETURN '2015-01-01';
	ELSE
		RETURN recent_date;
	END IF;
    END; //
DELIMITER ;