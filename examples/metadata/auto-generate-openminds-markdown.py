#!/usr/bin/env python3
"""
Fetch openMINDS valid values and descriptions from GitHub, then generate
supported-metadata.md.

Fetches JSON-LD instance files from the openMINDS_instances repository and
property descriptions from the openMINDS schema repository, then writes a
markdown reference document.

Usage:
    python metadata-script.py

Output: supported-metadata.md
"""

import json
import urllib.request
import urllib.error
from pathlib import Path

GITHUB_API = "https://api.github.com"
INSTANCES_REPO = "openMetadataInitiative/openMINDS_instances"
SCHEMAS_REPO = "openMetadataInitiative/openMINDS"
SCHEMAS_RAW = (
    f"https://raw.githubusercontent.com/{SCHEMAS_REPO}/main/schemas/latest"
)

# Schemas that contain the property descriptions we need.
SCHEMA_SOURCES = [
    "core/products/datasetVersion.schema.omi.json",
    "core/research/subject.schema.omi.json",
    "core/research/subjectState.schema.omi.json",
]

# Type-level schemas (description field on the schema itself, e.g.
# "Structured information on the species.").  Used as a second source
# when a property description is not available.
TYPE_SCHEMAS = {
    "species": "controlledTerms/species.schema.omi.json",
    "biologicalSex": "controlledTerms/biologicalSex.schema.omi.json",
    "technique": "controlledTerms/technique.schema.omi.json",
    "ageCategory": "controlledTerms/ageCategory.schema.omi.json",
    "measuredQuantity": "controlledTerms/measuredQuantity.schema.omi.json",
    "experimentalApproach": (
        "controlledTerms/experimentalApproach.schema.omi.json"
    ),
    "coordinateSpace": (
        "SANDS/atlas/commonCoordinateFramework.schema.omi.json"
    ),
}

# Fallback descriptions for properties that have no description in any
# openMINDS schema.  These are written by hand based on the openMINDS
# documentation and the BrainGlobe context.
FALLBACK_DESCRIPTIONS = {
    "experimentalApproach": (
        "The overarching scientific domain or methodological "
        "approach of the dataset."
    ),
    "measuredQuantity": (
        "What the voxel values in a 3D volume actually represent."
    ),
    "coordinateSpace": (
        "The reference coordinate space the volume is registered to."
    ),
    "anatomicalLocation": (
        "Specific brain regions tied to the experiment (e.g., a viral "
        "injection site, a tumor location, or an ROI)."
    ),
}

# Each entry defines one metadata field for the markdown output.
TERMS = [
    {
        "kwarg": "species",
        "openminds_property": "species",
        "openminds_url": "https://openminds.om-i.org/types/Species",
        "path": "instances/latest/terminologies/species",
        "name_key": "name",
    },
    {
        "kwarg": "atlas_space",
        "openminds_property": "coordinateSpace",
        "openminds_url": (
            "https://openminds.om-i.org/types/CommonCoordinateSpace"
        ),
        "path": "instances/latest/terminologies/commonCoordinateSpace",
        "fallback_paths": [
            "instances/v4.0/commonCoordinateSpaces",
            "instances/latest/commonCoordinateSpaces",
        ],
        "name_key": "fullName",
    },
    {
        "kwarg": "technique",
        "openminds_property": "technique",
        "openminds_url": "https://openminds.om-i.org/types/Technique",
        "path": "instances/latest/terminologies/technique",
        "name_key": "name",
        "collapsible": True,
    },
    {
        "kwarg": "experimental_approach",
        "openminds_property": "experimentalApproach",
        "openminds_url": (
            "https://openminds.om-i.org/types/ExperimentalApproach"
        ),
        "path": "instances/latest/terminologies/experimentalApproach",
        "name_key": "name",
    },
    {
        "kwarg": "anatomical_target",
        "openminds_property": "anatomicalLocation",
        "openminds_url": (
            "https://openminds.om-i.org/props/anatomicalLocation"
        ),
        "path": None,
        "name_key": None,
        "free_text": (
            'Free text (atlas-specific region acronyms, '
            'e.g. "MOp", "VISp", "amygdala")'
        ),
    },
    {
        "kwarg": "developmental_stage",
        "openminds_property": "ageCategory",
        "openminds_url": "https://openminds.om-i.org/types/AgeCategory",
        "path": "instances/latest/terminologies/ageCategory",
        "name_key": "name",
    },
    {
        "kwarg": "biological_sex",
        "openminds_property": "biologicalSex",
        "openminds_url": "https://openminds.om-i.org/types/BiologicalSex",
        "path": "instances/latest/terminologies/biologicalSex",
        "name_key": "name",
    },
    {
        "kwarg": "measured_quantity",
        "openminds_property": "measuredQuantity",
        "openminds_url": (
            "https://openminds.om-i.org/types/MeasuredQuantity"
        ),
        "path": "instances/latest/terminologies/measuredQuantity",
        "name_key": "name",
    },
]


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def github_api_get(endpoint):
    """Make a GET request to the GitHub API and return parsed JSON."""
    url = f"{GITHUB_API}/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "brainglobe-metadata-script")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_json(url):
    """Download and parse a JSON file from a URL."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "brainglobe-metadata-script")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------------------
# Fetch descriptions from openMINDS schemas
# ---------------------------------------------------------------------------
def fetch_property_descriptions():
    """
    Fetch property descriptions from openMINDS schema files.

    Tries three sources in order of preference:
    1. Property-level descriptions from parent schemas (e.g. datasetVersion)
    2. Type-level ``description`` field from controlled-term schemas
    3. Hand-written fallback descriptions

    Returns a dict mapping openMINDS property name -> description string.
    """
    descriptions = {}

    # 1. Property descriptions from parent schemas
    for schema_path in SCHEMA_SOURCES:
        url = f"{SCHEMAS_RAW}/{schema_path}"
        print(f"  Fetching schema: {schema_path}")
        try:
            schema = fetch_json(url)
        except urllib.error.HTTPError as e:
            print(f"    WARNING: Could not fetch {schema_path}: {e}")
            continue

        for prop_key, prop_val in schema.get("properties", {}).items():
            prop_name = prop_key.rsplit("/", 1)[-1]
            desc = prop_val.get("description")
            if desc and prop_name not in descriptions:
                descriptions[prop_name] = desc

    # 2. Type-level descriptions from controlled-term schemas
    for prop_name, schema_path in TYPE_SCHEMAS.items():
        if prop_name in descriptions:
            continue
        url = f"{SCHEMAS_RAW}/{schema_path}"
        print(f"  Fetching type schema: {schema_path}")
        try:
            schema = fetch_json(url)
            desc = schema.get("description")
            if desc:
                descriptions[prop_name] = desc
        except urllib.error.HTTPError as e:
            print(f"    WARNING: Could not fetch {schema_path}: {e}")

    # 3. Hand-written fallbacks
    for prop_name, desc in FALLBACK_DESCRIPTIONS.items():
        if prop_name not in descriptions:
            descriptions[prop_name] = desc
            print(f"  Using fallback description for: {prop_name}")

    return descriptions


# ---------------------------------------------------------------------------
# Fetch valid values from openMINDS instances
# ---------------------------------------------------------------------------
def list_jsonld_files(repo_path):
    """List .jsonld files in a GitHub repo directory, returning download URLs."""
    endpoint = f"repos/{INSTANCES_REPO}/contents/{repo_path}"
    try:
        contents = github_api_get(endpoint)
    except urllib.error.HTTPError as e:
        print(f"    WARNING: Could not list {repo_path}: {e}")
        return []

    return [
        item["download_url"]
        for item in contents
        if item["name"].endswith(".jsonld")
    ]


def extract_name(instance, name_key):
    """Extract the human-readable name from a JSON-LD instance."""
    val = instance.get(name_key)
    if val:
        return val
    for prefix in [
        "https://openminds.ebrains.eu/vocab/",
        "https://openminds.om-i.org/props/",
    ]:
        val = instance.get(prefix + name_key)
        if val:
            return val
    return None


def fetch_values_for_term(term):
    """Fetch all valid values for a single term from GitHub."""
    if term.get("free_text"):
        return None

    paths_to_try = [term["path"]]
    if "fallback_paths" in term:
        paths_to_try.extend(term["fallback_paths"])

    for path in paths_to_try:
        print(f"    Trying {path}...")
        urls = list_jsonld_files(path)
        if urls:
            print(f"    Found {len(urls)} instance files at {path}")
            break
    else:
        print(f"    No instance files found")
        return []

    names = []
    for url in urls:
        try:
            instance = fetch_json(url)
            name = extract_name(instance, term["name_key"])
            if name:
                names.append(name)
        except Exception as e:
            print(f"    WARNING: Could not fetch {url}: {e}")

    return sorted(names)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------
def generate_markdown(results, descriptions):
    """Generate the supported-metadata.md content."""
    lines = ["# Supported Metadata Fields"]

    for term, values in results:
        kwarg = term["kwarg"]
        prop = term["openminds_property"]

        # Look up the description from schemas
        description = descriptions.get(prop, "")

        openminds_url = term.get("openminds_url", "")

        lines.append("")
        lines.append(f"## `{kwarg}`")
        if description:
            lines.append("")
            lines.append(description)
        if openminds_url:
            lines.append("")
            lines.append(f"openMINDS type: [{openminds_url}]({openminds_url})")

        if term.get("free_text"):
            lines.append("")
            lines.append(f"**Valid values:** {term['free_text']}")
        elif values:
            count = len(values)
            value_str = ", ".join(values)

            if term.get("collapsible"):
                lines.append("")
                lines.append("<details>")
                lines.append(
                    f"<summary><strong>"
                    f"Valid values ({count})"
                    f"</strong></summary>"
                )
                lines.append("")
                lines.append(value_str)
                lines.append("")
                lines.append("</details>")
            else:
                lines.append("")
                lines.append(f"**Valid values ({count}):** {value_str}")
        else:
            lines.append("")
            lines.append("**Valid values:** None found")

        lines.append("")
        lines.append("---")

    # Remove trailing separator
    if lines[-1] == "---":
        lines.pop()
        lines.pop()

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Fetching openMINDS metadata from GitHub")
    print("=" * 60)

    # 1. Fetch property descriptions from schemas
    print("\n[Fetching property descriptions]")
    descriptions = fetch_property_descriptions()
    print(f"  Found descriptions for: {', '.join(sorted(descriptions))}")

    # 2. Fetch valid values for each term
    print()
    results = []
    for term in TERMS:
        kwarg = term["kwarg"]
        print(f"[{kwarg}]")
        values = fetch_values_for_term(term)
        if values is not None:
            print(f"    -> {len(values)} values")
        else:
            print(f"    -> free text (no controlled vocabulary)")
        results.append((term, values))

    # 3. Write markdown
    output_path = Path(__file__).parent / "supported-metadata.md"
    md = generate_markdown(results, descriptions)
    output_path.write_text(md, encoding="utf-8")
    print(f"\nWritten to: {output_path}")

    # 4. Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for term, values in results:
        prop = term["openminds_property"]
        desc = descriptions.get(prop, "(no description)")
        if values is None:
            count = "free text"
        else:
            count = f"{len(values)} values"
        print(f"  {term['kwarg']}: {count}")
        print(f"    Description: {desc}")


if __name__ == "__main__":
    main()
