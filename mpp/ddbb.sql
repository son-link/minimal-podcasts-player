BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "podcasts" (
	"idPodcast"	INTEGER,
	"title"	TEXT NOT NULL,
	"url"	TEXT NOT NULL,
	"cover"	TEXT,
	"lastUpdate"	INTEGER,
	"pageUrl"	TEXT,
	"description"	TEXT,
	PRIMARY KEY("idPodcast" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "episodes" (
	"idEpisode"	INTEGER,
	"idPodcast"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"url"	TEXT NOT NULL,
	"date"	INTEGER NOT NULL,
	"totalTime"	INTEGER,
	PRIMARY KEY("idEpisode" AUTOINCREMENT)
);
COMMIT;
