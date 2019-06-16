-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jun 16, 2019 at 07:34 PM
-- Server version: 5.7.25
-- PHP Version: 7.1.23

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `songen`
--
CREATE DATABASE IF NOT EXISTS `songen` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `songen`;

-- --------------------------------------------------------

--
-- Table structure for table `english`
--

CREATE TABLE `english` (
  `id` int(6) UNSIGNED NOT NULL,
  `gid` mediumint(8) UNSIGNED NOT NULL,
  `verse` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tags` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ipa` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `english_metadata`
--

CREATE TABLE `english_metadata` (
  `id` smallint(5) UNSIGNED NOT NULL,
  `Author` varchar(800) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Birth` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Death` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Given` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Surname` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Copyright` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Language` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `LoC` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Num` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Subject` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Title` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `français`
--

CREATE TABLE `français` (
  `id` int(6) UNSIGNED NOT NULL,
  `fname` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ln` int(4) NOT NULL,
  `verse` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ipa` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `english`
--
ALTER TABLE `english`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `english_metadata`
--
ALTER TABLE `english_metadata`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `français`
--
ALTER TABLE `français`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `english`
--
ALTER TABLE `english`
  MODIFY `id` int(6) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `english_metadata`
--
ALTER TABLE `english_metadata`
  MODIFY `id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `français`
--
ALTER TABLE `français`
  MODIFY `id` int(6) UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
