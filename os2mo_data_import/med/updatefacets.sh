#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

# CLI="echo python mox_util.py cli"
CLI="python mox_util.py cli --mox-base http://localhost:8080"
${CLI} ensure-class-exists --bvn "HO-MED" --title "Hoved-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "FÆ-MED" --title "Fælles-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "FA-MED" --title "Fag-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "OM-MED" --title "Område-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "LO-MED" --title "Lokal-MED" --facet-bvn "org_unit_type"
${CLI} ensure-class-exists --bvn "PE-MED" --title "Personalemøder med MED-status" --facet-bvn "org_unit_type"

${CLI} ensure-class-exists --bvn "MED-Tillidsrepræsentant" --title "MED-Tillidsrepræsentant" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Arbejdsmiljørepræsentant" --title "MED-Arbejdsmiljørepræsentant" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Næstformand" --title "MED-Næstformand" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Formand" --title "MED-Formand" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Medlem" --title "MED-Medlem" --facet-bvn "association_type"
${CLI} ensure-class-exists --bvn "MED-Medlem-suppleant" --title "MED-Medlem-suppleant" --facet-bvn "association_type"

${CLI} ensure-class-exists --bvn "MED-enhed" --title "MED-enhed" --facet-bvn "org_unit_level"
