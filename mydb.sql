CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`Users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`Users` ;

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
DROP TABLE IF EXISTS `mydb`.`Stocks` ;

CREATE TABLE IF NOT EXISTS `mydb`.`Stocks` (
  `stock` VARCHAR(45) NOT NULL,
  `name` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`stock`),
  UNIQUE INDEX `stock_UNIQUE` (`stock` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Portfolio`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`Portfolio` ;

CREATE TABLE IF NOT EXISTS `mydb`.`Portfolio` (
  `user_id` INT NOT NULL,
  `stock` VARCHAR(45) NOT NULL,
  `p_bought_at` INT NOT NULL,
  `volume` INT NOT NULL,
  `d_bouth_at` DATE NOT NULL,
  PRIMARY KEY (`user_id`, `stock`),
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
-- Table `mydb`.`Historical_Data`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`Historical_Data` ;

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