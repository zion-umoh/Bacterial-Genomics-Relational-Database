import os
import re

def getOrganismFiles():
    input_dir = get_input_dir()

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Error: Could not locate 'input_files' folder at {input_dir}")
    
    return [
        f for f in os.listdir(input_dir)
        if not f.startswith(".") and os.path.isfile(os.path.join(input_dir, f))
    ]

def clean_sql_string(val):
    if not val:
        return ""
    return val.replace("'", "''")

def get_input_dir():
    script_path = os.path.abspath(__file__)

    input_dir = os.path.join(os.path.dirname(os.path.dirname(script_path)), "input_files")
    
    if not os.path.exists(input_dir):
        input_dir = os.path.join(os.path.dirname(script_path), "input_files")

    return input_dir

def generate_sql():
    files = getOrganismFiles()

    input_dir = get_input_dir()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "result.sql")


    expected_cols = 17  # Fallback standard GAF 2.0 column count
    for first_file in files:
        first_file_path = os.path.join(input_dir, first_file)
        if os.path.exists(first_file_path):
            with open(first_file_path, "r", encoding="utf-8") as f_test:
                for test_line in f_test:
                    if not test_line.startswith("!"):
                        expected_cols = len(test_line.strip().split("\t"))
                        break
            break


    # Generate organisms map
    organism_map = {}

    for f in files:

        taxon_match = re.search(r"[-_](\d+)\.gaf$", f)
        if not taxon_match:
            continue
        taxon_id = f"taxon:{taxon_match.group(1)}"
        
        # Extract and clean the Organism Name from the filename
        name_part = f.rsplit('.', 1)[0]               
        name_part = re.sub(r"[-_]\d+$", "", name_part)   
        name_part = name_part.replace("_ecocyc", "")    
        name_part = re.sub(r"_[0-9]+$", "", name_part)   
        organism_name = name_part.replace("_", " ")    
        
        organism_map[taxon_id] = organism_name

    unique_organisms, unique_proteins, unique_go_terms = set(), set(), set()

    organism_inserts, protein_inserts, go_term_inserts, annotation_inserts = [], [], [], []

    # Parse each GAF file
    
    for f in files:
        file_path = os.path.join(input_dir, f)
        print(f"(DEBUG) Parsing: {f}")

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # Skip comment lines
                if line.startswith("!"):
                    continue

                # Skip incomplete rows
                columns = line.strip().split("\t")
                if len(columns) < 15:
                    continue

                # Extract relevant fields
                protein_id = clean_sql_string(columns[1])
                symbol = clean_sql_string(columns[2])
                go_id = clean_sql_string(columns[4])
                reference = clean_sql_string(columns[5])
                evidence_code = clean_sql_string(columns[6])
                aspect = clean_sql_string(columns[8])
                protein_name = clean_sql_string(columns[9])
                protein_type = clean_sql_string(columns[11])
                taxon_field = clean_sql_string(columns[12]) 
                raw_date = clean_sql_string(columns[13])
                assigned_by = clean_sql_string(columns[14])
                taxon_id = taxon_field.split("|")[0]
                organism_name = organism_map.get(taxon_id, "Unknown Organism")

                sql_date = "NULL"
                if len(raw_date) == 8:
                    sql_date = f"'{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}'"

                # Insert organism if not already present
                if taxon_id not in unique_organisms:
                    unique_organisms.add(taxon_id)
                    organism_inserts.append(f"INSERT INTO organisms (taxon_id, organism_name) VALUES ('{taxon_id}', '{organism_name}');")

                # Insert protein if not already present
                if protein_id not in unique_proteins:
                    unique_proteins.add(protein_id)
                    protein_inserts.append(f"INSERT INTO proteins (protein_id, taxon_id, symbol, name, type) VALUES ('{protein_id}', '{taxon_id}', '{symbol}', '{protein_name}', '{protein_type}');")

                # Insert GO term if not already present
                if go_id not in unique_go_terms:
                    unique_go_terms.add(go_id)
                    go_term_inserts.append(f"INSERT INTO go_terms (go_id, aspect) VALUES ('{go_id}', '{aspect}');")

                # Insert annotation
                annotation_inserts.append(f"INSERT INTO annotations (protein_id, go_id, evidence_code, reference, assigned_by, date) VALUES ('{protein_id}', '{go_id}', '{evidence_code}', '{reference}', '{assigned_by}', {sql_date});")

    # Write SQL Statements to output file
    print(f"(DEBUG) Writing SQL statements to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as out:
                out.write("-- Cleanup existing tables\n")
                out.write("DROP TABLE IF EXISTS PROTEIN_GO_ANNOTATIONS;\n")
                out.write("DROP TABLE IF EXISTS GO_TERMS;\n")
                out.write("DROP TABLE IF EXISTS PROTEINS;\n")
                out.write("DROP TABLE IF EXISTS ORGANISMS;\n\n")

                # Create tables
                out.write("-- Create Schema\n")
                out.write(
                    "CREATE TABLE ORGANISMS (\n"
                    "    taxon_id VARCHAR(20) PRIMARY KEY,\n"
                    "    organism_name VARCHAR(100) NOT NULL\n"
                    ");\n\n"
                )


                out.write(
                    "CREATE TABLE PROTEINS (\n"
                    "    protein_id VARCHAR(15) PRIMARY KEY,\n"
                    "    taxon_id VARCHAR(20) NOT NULL,\n"
                    "    symbol VARCHAR(20),\n"
                    "    name VARCHAR(150),\n"
                    "    type VARCHAR(20),\n"
                    "    FOREIGN KEY (taxon_id) REFERENCES ORGANISMS(taxon_id)\n"
                    ");\n\n"
                )
                
                out.write(
                    "CREATE TABLE GO_TERMS (\n"
                    "    go_id CHAR(10) PRIMARY KEY,\n"
                    "    aspect CHAR(1) NOT NULL\n"
                    ");\n\n"
                )
                
                out.write(
                    "CREATE TABLE PROTEIN_GO_ANNOTATIONS (\n"
                    "    annotation_id INT AUTO_INCREMENT PRIMARY KEY,\n"
                    "    protein_id VARCHAR(15) NOT NULL,\n"
                    "    go_id CHAR(10) NOT NULL,\n"
                    "    evidence_code CHAR(3),\n"
                    "    reference VARCHAR(30),\n"
                    "    assigned_by VARCHAR(30),\n"
                    "    date DATE,\n"
                    "    FOREIGN KEY (protein_id) REFERENCES PROTEINS(protein_id),\n"
                    "    FOREIGN KEY (go_id) REFERENCES GO_TERMS(go_id)\n"
                    ");\n\n"
                )


                # Write insert statements
                out.write("-- Insert Organism Data\n")
                out.write("\n".join(organism_inserts) + "\n\n")
                
                out.write("-- Insert Protein Data\n")
                out.write("\n".join(protein_inserts) + "\n\n")
                
                out.write("-- Insert GO Term Data\n")
                out.write("\n".join(go_term_inserts) + "\n\n")
                
                out.write("-- Insert Annotations\n")
                out.write("\n".join(annotation_inserts) + "\n")


    print("Generation complete! result.sql is ready to execute.")


if __name__ == "__main__":
    generate_sql()

