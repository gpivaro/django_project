DROP TABLE IF EXISTS `analyticsapp_clientipaddress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analyticsapp_clientipaddress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ip_address` varchar(120) DEFAULT NULL,
  `country` varchar(120) DEFAULT NULL,
  `region` varchar(120) DEFAULT NULL,
  `city` varchar(120) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `timestamp` datetime(6) NOT NULL,
  `absolute_uri` varchar(300) DEFAULT NULL,
  `issecure` tinyint(1) DEFAULT NULL,
  `path` varchar(200) DEFAULT NULL,
  `useragent` longtext,
  `map_link` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;