-- Example 1: Bacterial Competence Query
SELECT o.taxon_id, o.organism_name, COUNT(a.annotation_id) AS competence_annotations_count
FROM ORGANISMS o
JOIN PROTEINS p ON o.taxon_id = p.taxon_id
JOIN PROTEIN_GO_ANNOTATIONS a ON p.protein_id = a.protein_id
WHERE a.go_id IN ('GO:0030420', 'GO:0045304', 'GO:0045808', 'GO:0045809')
GROUP BY o.taxon_id, o.organism_name
ORDER BY competence_annotations_count DESC;

-- Example 2


-- Example 3


-- Example 4


-- Example 5