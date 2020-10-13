#!/bin/bash

# CLI="echo python mox_util.py cli"
CLI="venv/bin/python os2mo_data_import/med/mox_util.py cli --mox-base http://localhost:8080"
${CLI} ensure-class-exists --bvn "Hoved-MED" --title "HO-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "Fælles-MED" --title "FÆ-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "Fag-MED" --title "FA-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "Område-MED" --title "OM-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "Lokal-MED" --title "LO-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "Personalemøder med MED-status" --title "PE-MED" --facet-bvn "org_unit_type"

${CLI} ensure-class-exists --bvn "MED-Tillidsrepræsentant" --title "MED-Tillidsrepræsentant" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Arbejdsmiljørepræsentant" --title "MED-Arbejdsmiljørepræsentant" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Næstformand" --title "MED-Næstformand" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Formand" --title "MED-Formand" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Medlem" --title "MED-Medlem" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Medlem-suppleant" --title "MED-Medlem-suppleant" --facet-bvn "association_type"

${CLI} ensure-class-exists --bvn "MED-enhed" --title "MED-enhed" --facet-bvn "org_unit_level"


 ${CLI} update-class-value --bvn "Hoved-MED"  --variable titel --new_value "Hoved-MED"
 ${CLI} update-class-value --bvn "Hoved-MED"  --variable brugervendtnoegle --new_value "HO-MED"
 ${CLI} update-class-value --bvn "Fælles-MED"  --variable titel --new_value "Fælles-MED"
 ${CLI} update-class-value --bvn "Fælles-MED"  --variable brugervendtnoegle --new_value "FÆ-MED"
 ${CLI} update-class-value --bvn "Fag-MED"  --variable titel --new_value "Fag-MED"
 ${CLI} update-class-value --bvn "Fag-MED"  --variable brugervendtnoegle --new_value "FA-MED"
 ${CLI} update-class-value --bvn "Område-MED"  --variable titel --new_value "Område-MED"
 ${CLI} update-class-value --bvn "Område-MED"  --variable brugervendtnoegle --new_value "OM-MED"
 ${CLI} update-class-value --bvn "Lokal-MED"  --variable titel --new_value "Lokal-MED"
 ${CLI} update-class-value --bvn "Lokal-MED"  --variable brugervendtnoegle --new_value "LO-MED"
 ${CLI} update-class-value --bvn "Personalemøder med MED-status"  --variable titel --new_value "Personalemøder med MED-status"
 ${CLI} update-class-value --bvn "Personalemøder med MED-status"  --variable brugervendtnoegle --new_value "PE-MED"


