-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema architong
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `architong` ;

-- -----------------------------------------------------
-- Schema architong
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `architong` DEFAULT CHARACTER SET utf8 ;
USE `architong` ;

-- -----------------------------------------------------
-- Table `architong`.`books`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `architong`.`books` ;

CREATE TABLE IF NOT EXISTS `architong`.`books` (
  `book_id` INT NOT NULL COMMENT '도서ID' AUTO_INCREMENT,
  `book_title` VARCHAR(255) NOT NULL COMMENT '도서명',
  `cover_path` VARCHAR(255) NULL COMMENT '표지 이미지 경로',
  `rls_yn` CHAR(10) NOT NULL DEFAULT 'Y' COMMENT '공개여부 (default Y : public, N: private)',
  `wrt_dt` DATETIME NULL COMMENT '작성일시',
  PRIMARY KEY (`book_id`)) COMMENT '도서'
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `architong`.`pages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `architong`.`pages` ;

CREATE TABLE IF NOT EXISTS `architong`.`pages` (
  `page_id` INT NOT NULL AUTO_INCREMENT,
  `book_id` INT NOT NULL COMMENT '도서ID(FK)',
  `parent_id` INT NULL COMMENT '부모페이지ID',
  `page_title` VARCHAR(255) NOT NULL COMMENT '페이지ID',
  `description` TEXT NULL COMMENT '본문(markdown form)',
  `wrt_dt` DATETIME NULL COMMENT '작성일시',
  `mdfcn_dt` DATETIME NULL COMMENT '수정일시',
  PRIMARY KEY (`page_id`),
  INDEX `book_id_idx` (`book_id` ASC) VISIBLE,
  CONSTRAINT `book_id`
    FOREIGN KEY (`book_id`)
    REFERENCES `architong`.`books` (`book_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION) COMMENT '페이지(문서)'
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
