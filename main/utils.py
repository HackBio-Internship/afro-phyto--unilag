import re
import csv
import requests
import unicodedata
import base64
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import AllChem
from django.conf import settings

def compute_lipinski_from_smiles(smiles: str) -> dict:
    if not smiles:
        return {}

    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return {}

        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        h_donors = Descriptors.NumHDonors(mol)
        h_acceptors = Descriptors.NumHAcceptors(mol)

        return {
            "smiles": smiles,
            "inchikey": Chem.MolToInchiKey(mol),
            "molecular_weight": mw,
            "logp": logp,
            "h_donors": h_donors,
            "h_acceptors": h_acceptors,
            "lipinski_pass": (
                mw <= 500 and
                logp <= 5 and
                h_donors <= 5 and
                h_acceptors <= 10
            ),
        }

    except Exception:
        return {}

def normalize_header(header):
    return header.strip().lower().replace("_", " ")

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

    name = unicodedata.normalize("NFKC", name)

    # Replace Greek symbols
    for greek_char, ascii_name in GREEK_MAP.items():
        name = name.replace(greek_char, ascii_name)

    # Normalize hyphens
    name = re.sub(r"[‐-–—]", "-", name)

    # Remove weird punctuation except hyphen
    name = re.sub(r"[^a-zA-Z0-9\s\-]", "", name)

    # Lowercase for consistency
    name = name.lower()

    # Clean spacing
    name = re.sub(r"\s+", " ", name).strip()

    return name

def smiles_to_sdf(smiles: str) -> str:
    pass


def run_diffdock(protein_pdb, ligand_text, ligand_type, num_poses=10, steps=18):
    pass