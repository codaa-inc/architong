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
  `author_id` VARCHAR(150) NOT NULL COMMENT '저자명',
  `cover_path` VARCHAR(255) NULL COMMENT '표지 이미지 경로',
  `rls_yn` CHAR(10) NOT NULL DEFAULT 'Y' COMMENT '공개여부 (default Y : public, N: private)',
  `like_cnt` INT COMMENT '좋아요',
  `wrt_dt` DATETIME NULL COMMENT '작성일시',
  `codes_yn` CHAR(10) NULL DEFAULT 'N' COMMENT '법규/일반문서 구분(default N: 일반문서, Y: 법규)',
  PRIMARY KEY (`book_id`)) COMMENT '도서'
ENGINE = InnoDB;

INSERT INTO books (book_id, book_title, author_id, wrt_dt) VALUES (0, '건축법 [시행 2021. 4. 1.] [법률 제17171호, 2020. 3. 31., 타법개정]', 'codaa_', '2021.04.01');

-- -----------------------------------------------------
-- Table `architong`.`pages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `architong`.`pages` ;

CREATE TABLE IF NOT EXISTS `architong`.`pages` (
  `page_id` INT NOT NULL AUTO_INCREMENT COMMENT '페이지ID',
  `book_id` INT NOT NULL COMMENT '도서ID(FK)',
  `page_title` VARCHAR(255) NOT NULL COMMENT '페이지제목',
  `parent_id` INT NULL DEFAULT '0' COMMENT '부모페이지ID(default 0 : 최상위페이지)',
  `depth` INT NULL DEFAULT '0' COMMENT '페이지 레벨',
  `description` TEXT NULL COMMENT '본문(markdown form)',
  `wrt_dt` DATETIME NULL COMMENT '작성일시',
  `mdfcn_dt` DATETIME NULL COMMENT '수정일시',
  PRIMARY KEY (`page_id`),
  INDEX `book_id_idx` (`book_id` ASC) VISIBLE) COMMENT '페이지(문서)'
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `architong`.`bookmark`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `architong`.`bookmark` ;

CREATE TABLE IF NOT EXISTS `architong`.`bookmark` (
  `bookmark_id` INT NOT NULL AUTO_INCREMENT COMMENT '북마크ID',
  `page_id` INT NOT NULL COMMENT '페이지ID',
  `username` VARCHAR(150) NOT NULL COMMENT '사용자ID',
  `reg_dt` DATETIME NULL COMMENT '등록일시',
  PRIMARY KEY (`bookmark_id`),
  INDEX `bookmark_id_idx` (`bookmark_id` ASC) VISIBLE) COMMENT '페이지(문서)'
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `architong`.`comments`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `architong`.`comments` ;

CREATE TABLE IF NOT EXISTS `architong`.`comments` (
  `comment_id` INT NOT NULL COMMENT '댓글ID',
  `page_id` INT NOT NULL COMMENT '원글 페이지ID (FK - Pages)',
  `parent_id` INT NOT NULL DEFAULT 0 COMMENT '부모댓글ID (default : 0)',
  `depth` INT NOT NULL DEFAULT 0 COMMENT '댓글 레벨 (default : 0)',
  `username` VARCHAR(150) NOT NULL COMMENT '등록자ID',
  `content` TEXT NULL COMMENT '댓글내용',
  `rls_yn` CHAR(10) NULL DEFAULT 'Y' COMMENT '공개여부(default : Y-공개/N-비공개)',
  `reg_dt` DATETIME NULL COMMENT '등록일시',
  PRIMARY KEY (`comment_id`),
  INDEX `comments_id_idx` (`comment_id` ASC) VISIBLE) COMMENT '댓글'
ENGINE = InnoDB;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;