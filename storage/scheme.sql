-- -------------------------------------------------------------
-- TablePlus 4.2.0(388)
--
-- https://tableplus.com/
--
-- Database: scraper
-- Generation Time: 2023-02-19 22:18:22.3900
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS `scraper` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

DROP TABLE IF EXISTS `annual_reports`;
CREATE TABLE `annual_reports` (
  `id` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `year` int(11) NOT NULL,
  `business_status` varchar(50) DEFAULT NULL,
  `number_of_employees` int(11) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `total_assets` double DEFAULT NULL,
  `total_owner_equity` double DEFAULT NULL,
  `total_sales` double DEFAULT NULL,
  `total_profit` double DEFAULT NULL,
  `income_in_total` double DEFAULT NULL,
  `net_profit` double DEFAULT NULL,
  `total_tax` double DEFAULT NULL,
  `total_liabilities` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_annual_reports__company` (`company`),
  CONSTRAINT `fk_annual_reports__company` FOREIGN KEY (`company`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `branches`;
CREATE TABLE `branches` (
  `id` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `person` varchar(100) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_branches__company` (`company`),
  CONSTRAINT `fk_branches__company` FOREIGN KEY (`company`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `changes`;
CREATE TABLE `changes` (
  `id` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `date` date DEFAULT NULL,
  `change_type` varchar(150) DEFAULT NULL,
  `before_c` longtext,
  `after_c` longtext,
  PRIMARY KEY (`id`),
  KEY `idx_changes__company` (`company`),
  CONSTRAINT `fk_changes__company` FOREIGN KEY (`company`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `companies`;
CREATE TABLE `companies` (
  `id` varchar(255) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `website` varchar(100) DEFAULT NULL,
  `ceo` varchar(100) DEFAULT NULL,
  `registered_capital` double DEFAULT NULL,
  `date_of_establishment` date DEFAULT NULL,
  `operating_status` varchar(20) DEFAULT NULL,
  `registration_number` varchar(20) DEFAULT NULL,
  `social_credit_code` varchar(20) DEFAULT NULL,
  `organization_code` varchar(20) DEFAULT NULL,
  `tax_registration_number` varchar(20) DEFAULT NULL,
  `company_type` varchar(100) DEFAULT NULL,
  `operating_period` varchar(75) DEFAULT NULL,
  `industry` varchar(20) DEFAULT NULL,
  `taxpayer_qualification` varchar(20) DEFAULT NULL,
  `approval_date` date DEFAULT NULL,
  `paid_in_capital` varchar(20) DEFAULT NULL,
  `staff_size` varchar(20) DEFAULT NULL,
  `insured_staff_size` varchar(20) DEFAULT NULL,
  `registration_authority` varchar(50) DEFAULT NULL,
  `english_name` varchar(100) DEFAULT NULL,
  `registered_address` varchar(100) DEFAULT NULL,
  `business_scope` longtext,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `foreign_investments`;
CREATE TABLE `foreign_investments` (
  `id` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `person` varchar(100) DEFAULT NULL,
  `registered_capital` double DEFAULT NULL,
  `ratio` double DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_foreign_investments__company` (`company`),
  CONSTRAINT `fk_foreign_investments__company` FOREIGN KEY (`company`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `main_staff`;
CREATE TABLE `main_staff` (
  `id` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `position` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_main_staff__company` (`company`),
  CONSTRAINT `fk_main_staff__company` FOREIGN KEY (`company`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `shareholders`;
CREATE TABLE `shareholders` (
  `id` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `ratio` double DEFAULT NULL,
  `capital` double DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_shareholders__company` (`company`),
  CONSTRAINT `fk_shareholders__company` FOREIGN KEY (`company`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
