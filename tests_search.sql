SELECT id, link, text FROM texts_table, to_tsquery('russian','репликация') as q 
WHERE to_tsvector('russian', text) @@ q
ORDER BY ts_rank(to_tsvector('russian', text), q) DESC;

SELECT * FROM texts_table WHERE text LIKE '%репликация%';
