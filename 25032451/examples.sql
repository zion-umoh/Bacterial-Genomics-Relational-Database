-- Example 1: Bacterial Competence Query
SELECT o.taxon_id, o.organism_name, COUNT(a.annotation_id) AS competence_annotations_count
FROM ORGANISMS o
JOIN PROTEINS p ON o.taxon_id = p.taxon_id
JOIN PROTEIN_GO_ANNOTATIONS a ON p.protein_id = a.protein_id
WHERE a.go_id IN ('GO:0030420', 'GO:0045304', 'GO:0045808', 'GO:0045809')
GROUP BY o.taxon_id, o.organism_name
ORDER BY competence_annotations_count DESC;

-- Example 2: Top 10 most heavily annotated proteins
SELECT 
    p.protein_id, 
    p.symbol, 
    p.name, 
    o.organism_name,
    COUNT(a.annotation_id) AS total_annotations
FROM PROTEINS p
JOIN ORGANISMS o ON p.taxon_id = o.taxon_id
JOIN PROTEIN_GO_ANNOTATIONS a ON p.protein_id = a.protein_id
GROUP BY p.protein_id, p.symbol, p.name, o.organism_name
ORDER BY total_annotations DESC
LIMIT 10;

-- Example 3: Protein Distribution per Organism
SELECT 
    o.taxon_id, 
    o.organism_name, 
    COUNT(p.protein_id) AS unique_protein_count
FROM ORGANISMS o
LEFT JOIN PROTEINS p ON o.taxon_id = p.taxon_id
GROUP BY o.taxon_id, o.organism_name
ORDER BY unique_protein_count DESC;


-- Example 4: Annotation Distribution by Aspect
SELECT 
    t.aspect,
    CASE 
        WHEN t.aspect = 'F' THEN 'Molecular Function'
        WHEN t.aspect = 'P' THEN 'Biological Process'
        WHEN t.aspect = 'C' THEN 'Cellular Component'
        ELSE 'Unknown'
    END AS aspect_name,
    COUNT(a.annotation_id) AS annotation_count
FROM GO_TERMS t
JOIN PROTEIN_GO_ANNOTATIONS a ON t.go_id = a.go_id
GROUP BY t.aspect
ORDER BY annotation_count DESC;


-- Example 5: Data Provenance
SELECT 
    a.assigned_by, 
    COUNT(a.annotation_id) AS contribution_count
FROM PROTEIN_GO_ANNOTATIONS a
GROUP BY a.assigned_by
ORDER BY contribution_count DESC;

