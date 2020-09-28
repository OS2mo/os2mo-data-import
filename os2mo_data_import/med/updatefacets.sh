#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

# CLI="echo python mox_util.py cli"
CLI="python mox_util.py cli --mox-base http://localhost:8080"
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
