-- 
--

DROP DATABASE IF EXISTS DBPodcasts;
CREATE DATABASE DBPodcasts;
GRANT ALL ON DBPodcasts.* TO 'manuel'@'localhost' IDENTIFIED BY 'hita';
USE DBPodcasts;
--
DROP TABLE IF EXISTS Podcasts;

CREATE TABLE Podcasts (
    fecha       DATE       , 
    titulo      VARCHAR(100) NOT NULL, 
    descripcion VARCHAR(1000), 
    duracion    VARCHAR(10), 
    link        VARCHAR(100),
    valoracion  TINYINT(3) DEFAULT NULL,
    comentarios VARCHAR(200),
    descargado  CHAR(0) DEFAULT NULL, 
    PRIMARY KEY (fecha)
);
 
