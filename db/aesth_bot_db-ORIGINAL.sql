-- phpMyAdmin SQL Dump
-- version 5.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Apr 13, 2022 at 08:49 PM
-- Server version: 8.0.19
-- PHP Version: 7.1.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `aesthetic-bot`
--

USE `aesthetic-bot`;

-- --------------------------------------------------------

--
-- Table structure for table `gen_levels`
--

CREATE TABLE `gen_levels` (
  `ID` int NOT NULL,
  `TILESET` varchar(100) NOT NULL,
  `ASCII_MAP` varchar(1000) NOT NULL,
  `MAP_SIZE` int NOT NULL,
  `TIME_MADE` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `EVALS` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `gen_levels`
--

INSERT INTO `gen_levels` (`ID`, `TILESET`, `ASCII_MAP`, `MAP_SIZE`, `TIME_MADE`, `EVALS`) VALUES
(27, 'zelda', 'cd0650\nef7401\n71006b\n000140\nd30003\n050a3a', 6, '2022-04-12 19:07:14', 0),
(28, 'pokemon', 'ba6650\naa05aa\naaaaaa\naaaaaa\n444aa6\n5058aa', 6, '2022-04-12 19:09:17', 0),
(29, 'pacman', '8ff0c7\nc77711\n111112\nb74761\nef11d1\nf313e1', 6, '2022-04-12 19:11:12', 1),
(30, 'amongus', 'bf5002\n005000\n008002\n008000\n008183\n06800d', 6, '2022-04-12 19:13:02', 1),
(31, 'dungeon', 'effcff\n05f8ff\nff50ff\n0f253c\n10ff00\n0bfff1', 6, '2022-04-12 19:15:05', 1),
(32, 'zelda', '999995\nb43000\nbbf895\n000010\n0407bb\n0851b0', 6, '2022-04-12 22:11:07', 0),
(33, 'pokemon', 'b7a0007\n4401999\n998d000\n1aa0108\nd9aa466\n0faaa06\n5aaaaa6', 7, '2022-04-12 22:13:06', 0),
(34, 'pacman', '3ea112\n81e111\n8111b1\nd1f12b\n11761e\n302011', 6, '2022-04-12 22:14:54', 1),
(35, 'amongus', 'e04888\n005800\n9aa0b6\nbf0080\n0c0888\n00080b', 6, '2022-04-12 22:17:06', 0),
(36, 'dungeon', 'ffffdf\ncf0888\nfffddf\n030000\n6000b8\n10b87f', 6, '2022-04-12 22:18:54', 0);

-- --------------------------------------------------------

--
-- Table structure for table `user_levels`
--

CREATE TABLE `user_levels` (
  `ID` int NOT NULL,
  `TILESET` varchar(100) NOT NULL,
  `ASCII_MAP` varchar(1000) NOT NULL,
  `MAP_SIZE` int NOT NULL,
  `AUTHOR` varchar(200) DEFAULT NULL,
  `TIME_MADE` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `EVALS` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_levels`
--

INSERT INTO `user_levels` (`ID`, `TILESET`, `ASCII_MAP`, `MAP_SIZE`, `AUTHOR`, `TIME_MADE`, `EVALS`) VALUES
(4, 'pacman', 'b77600477a\n8211111128\n8147777618\n5111111115\n0113003110\n0118ff8110\n311c77d113\n8111111118\n8211111128\nc77600477d', 10, '@MasterMilkX', '2022-01-29 00:18:46', 1),
(6, 'pacman', 'b7776004777a\n821111111128\n814610014618\n811114611118\n513111111315\n01813ff31810\n01818ff81810\n3151c77d1513\n811111111118\n814614614618\n821111111128\nc7776004777d', 12, '@MasterMilkX', '2022-01-29 00:23:20', 1),
(7, 'amongus', '7109a9a9a000\n40000d0001c7\n003002000000\n0bb000c08888\n00f100008320\n19a0888010db\n0d0010808000\n888800808888\n5c5802800710\n0000008100c5\n10e800800003\n4638002000f5', 12, '@MasterMilkX', '2022-01-29 00:23:48', 1),
(8, 'dungeon', 'ffefffdfffff\r\nf500500f034f\r\nf590c20fb33f\r\nf0000000000f\r\nf208010fa07f\r\nf000000ffffe\r\nd07b0009000d\r\nffff0200020f\r\nf5039000000f\r\nf86f00000b8f\r\nf8cf5a10088f\r\nfefffffffeff', 12, '@MasterMilkX', '2022-01-29 00:24:13', 1),
(9, 'pokemon', 'aaaaaaaaaaaa\na3990000cc0a\na0000008de3a\na0200666600a\na5000600005a\na0000602000a\na0500600000a\na40006000bba\na74666666bba\na4200000000a\na0000050020a\naaaaaaaaa77a', 12, '@MasterMilkX', '2022-01-29 00:24:29', 0),
(10, 'zelda', '999999999999\n8cd00000cd03\n0ef00075ef50\n00000100a070\n020100018500\n000000200001\n033300000444\n037300044446\n23030104466b\n0000000446bb\ncd0000446bbb\nef277346bbbb', 12, '@MasterMilkX', '2022-01-29 00:24:45', 0),
(11, 'pokemon', '999999999999\r\n0000a000fa03\r\n0a000000a050\r\n000001a00070\r\na20100010500\r\n00000a200001\r\n03330000a444\r\n037300044446\r\n230301a4446b\r\n0000000444bb\r\nc00000446bbb\r\nef277346bbbb', 10, '@MasterMilkX', '2022-01-31 19:50:50', 0),
(13, 'zelda', '30002031\n0cd01000\n9ef79999\n0000300a\n00200000\n30000cd0\n00007ef7\n10000002', 8, '@MasterMilkX', '2022-02-14 19:13:00', 0),
(14, 'zelda', '0400610050\n34cd43000a\n14ef400000\n0464464cd0\n5044714ef0\n0100004005\n000cd04100\n300ef06403\nbb000704cd\nbbb00504ef', 10, '@MasterMilkX', '2022-02-14 19:14:24', 0),
(15, 'pokemon', 'aaaaaaaaaa\naaaaaaaa00\na44fa76050\n4444a66020\n2444a05000\n0044aaaaa0\n5004aaaaa0\n0000308a03\naa00005a05\n3050000000', 10, '@MasterMilkX', '2022-02-14 19:15:51', 0),
(16, 'pacman', 'b777777a\n8f111118\n97614979\n51111512\n21311113\n97961479\n811111f8\nc777777d', 8, '@MasterMilkX', '2022-02-14 19:18:26', 0),
(17, 'pacman', 'b777777777a\r\n81111111118\r\n814afefb618\r\n81250005218\r\n51000300015\r\n01477977610\r\n31000500013\r\n81230003218\r\n814dfefc618\r\n81111111118\r\nc777777777d', 11, '@MasterMilkX', '2022-02-14 19:21:32', 0),
(18, 'amongus', '88888888888\n509a0c09a03\n50000d00000\n5e0000100bf\n51400009a00\n50000000007\n88888088888\n1bc28083475\n02e08082004\n0000808f600\n30010000010', 11, '@MasterMilkX', '2022-02-14 19:23:36', 0),
(19, 'dungeon', 'ffeffffffef\r\nf450908f8cc\r\nf000020f888\r\nfb20100ffdf\r\nf00000b0091\r\nffeff000000\r\nf752f10ffef\r\nf890f09000a\r\nf300f002000\r\nf000000f333\r\nfa00b00f876', 11, '@MasterMilkX', '2022-02-14 19:26:11', 0),
(20, 'dungeon', 'ffffffff\r\nffec99cf\r\nf4f9869f\r\nf0f0000f\r\nfdf2502f\r\nf0fff3ff\r\nf00a018f\r\nf510200d', 8, '@MasterMilkX', '2022-02-14 19:27:27', 0),
(21, 'amongus', '88888888\n809a0238\n80fd0068\n8c000108\n81000008\n0000bbb8\ne0100d48\n80000058', 8, '@MasterMilkX', '2022-02-14 19:29:09', 0),
(22, 'pokemon', 'aaaaaaaa\nafaacc3a\na44ade24\na44a0304\na0f9099a\na500200a\nabbf0020\nabbb050a', 8, '@MasterMilkX', '2022-02-14 21:42:26', 0),
(23, 'zelda', '707bbbbb\n80bbb000\n03bb0cd2\n001baef0\n201b0003\n070bb464\n0107bbbb\n00003bbb', 8, '@MasterMilkX', '2022-02-14 21:43:43', 0),
(24, 'pokemon', '01006de80a\na007666666\n0000600102\n0cc0600700\n3de8609999\n0666609f00\n5000609cc1\n0010608de0\na020666600\nba446444aa', 10, '@MasterMilkX', '2022-03-08 00:02:21', 0),
(25, 'amongus', '500cb888\n52000002\n508020d3\n88888888\n709a9a00\n4001000e\n0b00cb01\n36001f00', 8, '@MasterMilkX', '2022-03-15 15:55:46', 0),
(27, 'dungeon', 'ffedeffffeff\r\nf02055ff88cf\r\nf90a05ff568f\r\nf00000ff200f\r\ne002b03000be\r\nf5000030900f\r\nf09000ff002f\r\nffffffff000f\r\nffeffefffdff\r\nec0a052a000e\r\nf0000900040f\r\nf2900000b00f', 12, '@MasterMilkX', '2022-03-15 15:58:23', 0),
(28, 'zelda', 'cdcdcdcdcd\nefefefefef\ncd020002cd\nef300010ef\ncd00bb03cd\nef20bb00ef\ncd000052cd\nef100000ef\ncdcd30cdcd\nefef01efef', 10, '@MasterMilkX', '2022-03-15 19:10:55', 0),
(29, 'pacman', 'b77600477a\n8211111128\n811b77a118\n9a1c77d1b9\n88111f1188\n8811f11188\n9d1b77a1c9\n811c77d118\n8211111128\nc77600477d', 10, '@MasterMilkX', '2022-03-15 19:14:49', 0),
(30, 'dungeon', 'fffffff\nfc0508f\nf70006f\nfffdfff\n42000a0\n8900b02\n0080005', 7, '@MasterMilkX', '2022-03-15 19:17:16', 0),
(31, 'zelda', 'bbbbb67e\nbbbbb441\nbbbb6400\nbb764412\nb644400c\n644100ae\ncd00cdcd\nef20efef', 8, '@MasterMilkX', '2022-03-21 16:58:20', 0),
(32, 'amongus', '8888888888\n8360b4789a\n8d00007801\n820cc04800\n8000000802\n8000040832\n8555888888\n800009abf0\n810e000001\n80000e0100', 10, '@MasterMilkX', '2022-03-21 19:05:32', 0),
(33, 'pokemon', 'aaaaaa\n0cc200\n8de001\n666666\n909999\n444444', 6, '@MasterMilkX', '2022-03-25 17:59:10', 0),
(34, 'pacman', 'b7777a\n82ff28\n821128\nca11bd\n181181\n181181', 6, '@MasterMilkX', '2022-03-25 18:01:16', 0),
(35, 'amongus', '0f88c0\n4388d0\n888888\n9a8820\ne06320\n000000', 6, '@MasterMilkX', '2022-03-25 18:02:04', 0),
(36, 'dungeon', 'f600af\nf0100f\nf333ff\nf802cf\nffb00f\nfd002f', 6, '@MasterMilkX', '2022-03-25 18:02:45', 0),
(37, 'zelda', '9cd999\n2ef030\n00000c\ncd007e\nef0100\n0a0003', 6, '@MasterMilkX', '2022-03-25 18:04:03', 0),
(38, 'pokemon', 'fbbb40074\n44040cc40\n99998de99\n001000066\naa7440006\naaaa44010\naaaaa4400\n4faa44006\n444440166', 9, '@MasterMilkX', '2022-03-25 18:05:15', 0),
(39, 'pacman', 'b7777777777a\n811111111128\n81b777a1b77e\n818f1151ef18\n81e7a111ca18\n8152e7611e18\n811181111518\ne77ed14a1118\n8128f12e7618\n814e777d1118\n811111111328\nc77777777e7d', 12, '@MasterMilkX', '2022-03-25 18:12:20', 0),
(40, 'amongus', '8888888888\n6f32100500\n002000050e\n0000000810\n5555588888\n00000839a0\n0100482001\n0004780bbb\n0e004800d0\n0001050000', 10, '@MasterMilkX', '2022-03-25 18:13:45', 0),
(41, 'dungeon', 'efffeefffe\ncc888888cc\nfffeddefff\n2100000902\n60b0021090\n0020900005\nffffffffff\ndfe4ff4efd\n0a20332600\n50703300a0', 10, '@MasterMilkX', '2022-03-25 18:15:48', 0),
(42, 'pokemon', '7aaaaaaaaa\n7aaa0cc0aa\naaaa8de0aa\n4400000004\nb444666604\nbb466cc66b\nbaaa6de6aa\naaaa6666aa\n23aa766faa\n321aa66aaa', 10, '@MasterMilkX', '2022-03-25 18:56:54', 0),
(43, 'zelda', '99cd999\n3aef8a9\n0070039\n3a0a3a9\n0030009\n0a0a0a9\n0000009', 7, '@MasterMilkX', '2022-03-25 18:58:23', 0),
(44, 'pacman', '1111111\n1b777a1\n152f251\n1111111\n1147611\n3211123\nc61114d', 7, '@MasterMilkX', '2022-03-25 18:59:40', 0),
(45, 'amongus', '32d001c\n9ac0b0e\n1000000\n8885588\n848009a\n06e00bf\n7010000', 7, '@MasterMilkX', '2022-03-25 19:01:12', 0),
(46, 'dungeon', 'ffedeff\nf200a0f\nf03332f\nf380b3f\nf30823f\n1033305\n9000010', 7, '@MasterMilkX', '2022-03-25 19:02:30', 0),
(47, 'zelda', '030003\n000020\n30cd30\n07ef00\n200000\n030003', 6, '', '2022-04-12 20:30:13', 0);

-- --------------------------------------------------------

--
-- Table structure for table `vote_pairs`
--

CREATE TABLE `vote_pairs` (
  `PAIR_ID` int NOT NULL,
  `USER_LEVEL_ID` int NOT NULL,
  `GEN_LEVEL_ID` int NOT NULL,
  `REAL_LEVEL_AB` tinytext NOT NULL,
  `TIME_MADE` timestamp NOT NULL,
  `TIME_FINISH` timestamp NULL DEFAULT NULL,
  `A_VOTES` int DEFAULT '0',
  `B_VOTES` int DEFAULT '0',
  `TWITTER_ID` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `vote_pairs`
--

INSERT INTO `vote_pairs` (`PAIR_ID`, `USER_LEVEL_ID`, `GEN_LEVEL_ID`, `REAL_LEVEL_AB`, `TIME_MADE`, `TIME_FINISH`, `A_VOTES`, `B_VOTES`, `TWITTER_ID`) VALUES
(53, 4, 29, 'B', '2022-04-12 22:35:01', '2022-04-12 22:46:05', 0, 1, '1514009440231514121'),
(55, 6, 34, 'A', '2022-04-12 22:56:04', '2022-04-12 23:06:31', 1, 0, '1514014519139487747'),
(56, 7, 30, 'A', '2022-04-12 23:09:32', '2022-04-12 23:19:44', 0, 1, '1514017908267098117'),
(57, 8, 31, 'B', '2022-04-13 18:34:41', '2022-04-13 18:44:55', 0, 1, '1514311130264522754');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `gen_levels`
--
ALTER TABLE `gen_levels`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `ID` (`ID`);

--
-- Indexes for table `user_levels`
--
ALTER TABLE `user_levels`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `ID` (`ID`);

--
-- Indexes for table `vote_pairs`
--
ALTER TABLE `vote_pairs`
  ADD PRIMARY KEY (`PAIR_ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `gen_levels`
--
ALTER TABLE `gen_levels`
  MODIFY `ID` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `user_levels`
--
ALTER TABLE `user_levels`
  MODIFY `ID` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;

--
-- AUTO_INCREMENT for table `vote_pairs`
--
ALTER TABLE `vote_pairs`
  MODIFY `PAIR_ID` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=58;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
