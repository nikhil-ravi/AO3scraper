CREATE TYPE "ratings_enum" AS ENUM (
  'Not Rated',
  'General Audiences',
  'Teen And Up Audiences',
  'Mature',
  'Explicit'
);

CREATE TYPE "warnings_enum" AS ENUM (
  'No Archive Warnings Apply',
  'Creator Chose Not To Use Archive Warnings',
  'Graphic Depictions Of Violence',
  'Major Character Death',
  'Underage',
  'Rape/Non-Con'
);

CREATE TYPE "category_enum" AS ENUM (
  'F/F',
  'F/M',
  'Gen',
  'M/M',
  'Multi',
  'Other'
);

CREATE TABLE "languages_list" (
  "id" SERIAL PRIMARY KEY UNIQUE,
  "name" varchar NOT NULL UNIQUE
);

CREATE TABLE "users" (
  "id" int PRIMARY KEY UNIQUE,
  "name" varchar UNIQUE NOT NULL,
  "joined" date NOT NULL
);

CREATE TABLE "works" (
  "id" int PRIMARY KEY UNIQUE,
  "url" varchar NOT NULL UNIQUE,
  "title" varchar NOT NULL,
  "summary" varchar,
  "language_id" int NOT NULL REFERENCES languages_list("id"),
  "rating_id" ratings_enum,
  "published" date,
  "status" date,
  "complete" boolean,
  "words" int,
  "chapters_published" int,
  "chapters_expected" int,
  "comments" int,
  "kudos" int,
  "bookmarks" int,
  "hits" int
);

CREATE TABLE "authors" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "user_id" int NOT NULL REFERENCES "users"("id"),
  UNIQUE ("work_id", "user_id")
);

CREATE TABLE "warnings" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "warning" warnings_enum NOT NULL,
	UNIQUE("work_id", "warning")
);

CREATE TABLE "category" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "category" category_enum NOT NULL,
	UNIQUE("work_id", "category")
);

CREATE TABLE "fandoms_list" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL
);

CREATE TABLE "fandoms" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "fandom_id" int NOT NULL REFERENCES "fandoms_list"("id"),
	UNIQUE("work_id", "fandom_id")
);

CREATE TABLE "relationships_list" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL
);

CREATE TABLE "relationships" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "relationship_id" int NOT NULL REFERENCES "relationships_list"("id"),
	UNIQUE("work_id", "relationship_id")
);

CREATE TABLE "characters_list" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL
);

CREATE TABLE "characters" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "character_id" int NOT NULL REFERENCES "characters_list"("id"),
	UNIQUE("work_id", "character_id")
);

CREATE TABLE "additional_tags_list" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar NOT NULL
);

CREATE TABLE "additional_tags" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "additional_tag_id" int NOT NULL REFERENCES "additional_tags_list"("id"),
	UNIQUE("work_id", "additional_tag_id")
);

CREATE TABLE "kudos" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "user_id" int NOT NULL REFERENCES "users"("id"),
	UNIQUE("work_id", "user_id")
);

CREATE TABLE "bookmarks" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "user_id" int NOT NULL REFERENCES "users"("id"),
	UNIQUE("work_id", "user_id")
);

CREATE TABLE "comments" (
  "work_id" int NOT NULL REFERENCES "works"("id"),
  "user_id" int NOT NULL REFERENCES "users"("id"),
  "comment" varchar,
	UNIQUE("work_id", "user_id")
);

