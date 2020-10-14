#!/bin/bash
## Script til opsætning til Viborgs MED-organisation

MOX_URL="${MOX_URL:-http://localhost:8080}"

CLI="venv/bin/python os2mo_data_import/med/mox_util.py cli --mox-base ${MOX_URL}"
# Organisation Unit Types
#------------------------
${CLI} ensure-class-exists --bvn "HO-MED" --title "Hoved-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "FÆ-MED" --title "Fælles-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "FA-MED" --title "Fag-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "OM-MED" --title "Område-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "LO-MED" --title "Lokal-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "PE-MED" --title "Personalemøder med MED-status" --facet-bvn "org_unit_type"

# Association Types
#------------------------
${CLI} ensure-class-exists --bvn "MED-Tillidsrepræsentant" --title "MED-Tillidsrepræsentant" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Arbejdsmiljørepræsentant" --title "MED-Arbejdsmiljørepræsentant" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Næstformand" --title "MED-Næstformand" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Formand" --title "MED-Formand" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Medlem" --title "MED-Medlem" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Medlem-suppleant" --title "MED-Medlem-suppleant" --facet-bvn "association_type"

# org_unit_level
#------------------------
${CLI} ensure-class-exists --bvn "MED-enhed" --title "MED-enhed" --facet-bvn "org_unit_level"

##Checks - only to test out new feature "ensure-class-value":
${CLI} ensure-class-value --bvn "HO-MED" --variable titel --new_value "Hoved-MED"
${CLI} ensure-class-value --bvn "Hoved-MED"  --variable brugervendtnoegle --new_value "HO-MED"
${CLI} ensure-class-value --bvn "FÆ-MED"  --variable titel --new_value "Fælles-MED2"
${CLI} ensure-class-value --bvn "FÆ-MED"  --variable titel --new_value "Fælles-MED"
${CLI} ensure-class-value --bvn "FÆ-MED"  --variable titel --new_value "Fælles-MED"

