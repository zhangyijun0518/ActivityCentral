DROP DATABASE IF EXISTS activitycentral;

CREATE DATABASE activitycentral;

DROP TABLE IF EXISTS `activitycentral`.`user`;

CREATE TABLE `activitycentral`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL COMMENT 'user email',
  `pwd` VARCHAR(100) NULL,
  `token` VARCHAR(100) NULL,
  `create` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'register time for the user',
  `token_time` INT NULL COMMENT 'expire time for token(consider move to redis when necessary)',
  `status` INT NULL DEFAULT 0 COMMENT 'user status: 0 not valid 1 valid',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC));