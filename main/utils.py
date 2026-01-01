import pubchempy as pcp
from rdkit import Chem
import re
import unicodedata

GREEK_MAP = {
    "α": "alpha",
    "β": "beta",
    "γ": "gamma",
    "δ": "delta",
    "Δ": "delta",
    "ε": "epsilon",
    "ζ": "zeta",
    "η": "eta",
    "θ": "theta",
    "ι": "iota",
    "κ": "kappa",
    "λ": "lambda",
    "μ": "mu",
    "ν": "nu",
    "ξ": "xi",
    "ο": "omicron",
    "π": "pi",
    "ρ": "rho",
    "σ": "sigma",
    "τ": "tau",
    "υ": "upsilon",
    "φ": "phi",
    "Φ": "phi",
    "χ": "chi",
    "ψ": "psi",
    "ω": "omega",
    "Ω": "omega",
}

def normalize_chemical_name(name: str) -> str:
    if not name:
        return ""

    # Normalize Unicode (important for mixed encodings)
    name = unicodedata.normalize("NFKC", name)

    # Replace Greek characters
    for greek_char, ascii_name in GREEK_MAP.items():
        name = name.replace(greek_char, ascii_name)

    # Normalize hyphens (PubChem is picky)
    name = re.sub(r"[‐-–—]", "-", name)

    # Remove extra whitespace
    name = re.sub(r"\s+", " ", name).strip()

    return name

def generate_smiles_from_name(compound_name: str) -> str:
    if not compound_name:
        return ""

    try:
        # Normalize name (Greek letters, Unicode, hyphens
        normalized_name = normalize_chemical_name(compound_name)

        # Query PubChem
        results = pcp.get_compounds(normalized_name, "name")
        if not results:
            return ""

        smiles = results[0].connectivity_smiles
        if not smiles:
            return ""

        # Canonicalize with RDKit
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            return Chem.MolToSmiles(mol)
        else:
            return ""

    except Exception as e:
        print(f"Error generating SMILES for {compound_name}: {e}")
        return ""