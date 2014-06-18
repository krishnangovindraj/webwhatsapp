-- phpMyAdmin SQL Dump
-- version 4.0.4
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 18, 2014 at 09:59 PM
-- Server version: 5.6.12-log
-- PHP Version: 5.4.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `webwhatsapp`
--
CREATE DATABASE IF NOT EXISTS `webwhatsapp` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `webwhatsapp`;

-- --------------------------------------------------------

--
-- Table structure for table `inbox`
--

CREATE TABLE IF NOT EXISTS `inbox` (
  `messageId` varchar(40) NOT NULL,
  `recipient` bigint(10) unsigned NOT NULL,
  `sender` bigint(20) NOT NULL,
  `message` text NOT NULL,
  `tstamp` int(10) unsigned NOT NULL,
  `seen` tinyint(1) NOT NULL,
  PRIMARY KEY (`messageId`),
  KEY `recipient` (`recipient`,`seen`),
  KEY `participants` (`recipient`,`sender`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `outbox`
--

CREATE TABLE IF NOT EXISTS `outbox` (
  `messageId` varchar(40) NOT NULL,
  `sender` bigint(20) unsigned NOT NULL,
  `recipient` bigint(20) unsigned NOT NULL,
  `message` text NOT NULL,
  `tstamp` int(10) unsigned NOT NULL,
  `status` tinyint(4) NOT NULL,
  `lastupdated` int(10) unsigned NOT NULL,
  PRIMARY KEY (`messageId`),
  KEY `tstamp` (`tstamp`),
  KEY `status_lastupdated` (`status`,`lastupdated`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `pythoninstances`
--

CREATE TABLE IF NOT EXISTS `pythoninstances` (
  `instanceId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `phone` bigint(10) unsigned NOT NULL,
  `procId` int(10) unsigned NOT NULL,
  `lastUpdated` int(10) unsigned NOT NULL,
  `status` tinyint(4) NOT NULL,
  `authStatus` tinyint(4) NOT NULL,
  PRIMARY KEY (`instanceId`),
  KEY `lastUpdated` (`lastUpdated`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `email` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `password` char(32) NOT NULL,
  `whatsapp_pass` text NOT NULL,
  `phone` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
