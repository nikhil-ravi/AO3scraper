MATCH (n) DETACH DELETE n; 
load csv WITH headers from 'file:///works_list.csv' AS row merge (w: Work {id: toInteger(row.id), url: row.url, title: row.title, summary: coalesce(row.summary, ""), rating: row.rating, published: date(row.published), status: date(row.status), complete: toBoolean(row.complete), words: toInteger(row.words), chapters_published: toInteger(row.chapters_published), chapters_expected: coalesce(toInteger(row.chapters_expected), -1), comments: toInteger(row.comments), kudos: toInteger(row.kudos), bookmarks: toInteger(row.bookmarks), hits: toInteger(row.hits)})
RETURN count(w); 
create index if NOT exists for (w:Work) on (w.id);

load csv WITH headers from 'file:///users_list.csv' AS row merge (w: User {name: row.name})
RETURN count(w); 
create index if NOT exists for (u:User) on (u.name); 
LOAD CSV WITH HEADERS FROM 'file:///authors.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (u:User {name: row.name}) MERGE (w)-[:AUTHORED_BY]->(u)
RETURN *; 

load csv WITH headers from 'file:///languages_list.csv' AS row merge (l:Language {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Language) on (l.id); 
LOAD CSV WITH HEADERS FROM 'file:///languages.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Language {id: row.language_id}) MERGE (w)-[:IN_LANGUAGE]->(l)
RETURN *;

LOAD CSV WITH headers from 'file:///warnings_list.csv' AS row merge (l:Warning {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Warning) on (l.id);
LOAD CSV WITH HEADERS FROM 'file:///warnings.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Warning {id: row.warning_id}) MERGE (w)-[:HAS_WARNING]->(l)
RETURN *;

LOAD CSV WITH headers from 'file:///category_list.csv' AS row merge (l:Category {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Category) on (l.id);
LOAD CSV WITH HEADERS FROM 'file:///categories.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Category {id: row.category_id}) MERGE (w)-[:IS_IN_CATEGORY]->(l)
RETURN *;

LOAD CSV WITH headers from 'file:///fandoms_list.csv' AS row merge (l:Fandom {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Fandom) on (l.id);
LOAD CSV WITH HEADERS FROM 'file:///fandoms.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Fandom {id: row.fandom_id}) MERGE (w)-[:IS_IN_FANDOM]->(l)
RETURN *;

LOAD CSV WITH headers from 'file:///relationships_list.csv' AS row merge (l:Relationship {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Relationship) on (l.id);
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Relationship {id: row.relationship_id}) MERGE (w)-[:HAS_RELATIONSHIP]->(l)
RETURN *;

LOAD CSV WITH headers from 'file:///characters_list.csv' AS row merge (l:Character {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Character) on (l.id);
LOAD CSV WITH HEADERS FROM 'file:///characters.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Character {id: row.character_id}) MERGE (w)-[:HAS_CHARACTER]->(l)
RETURN *;

LOAD CSV WITH headers from 'file:///additional_tags_list.csv' AS row merge (l:Tag {id: row.id, name: row.name})
RETURN count(l); 
create index if NOT exists for (l:Tag) on (l.id);
LOAD CSV WITH HEADERS FROM 'file:///additional_tags.csv' AS row
MATCH (w:Work {id: toInteger(row.work_id)})
MATCH (l:Tag {id: row.additional_tag_id}) MERGE (w)-[:HAS_TAG]->(l)
RETURN *;