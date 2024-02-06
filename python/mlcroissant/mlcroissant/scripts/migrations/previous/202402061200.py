"""Migration: citation to citeAs."""


def up(json_ld):
    """Up migration for citation -> citeAs."""
    if "citation" in json_ld:
        json_ld["citeAs"] = json_ld["citation"]
        print("WEEEEEEE\n\n", json_ld["citeAs"])
        del json_ld["citation"]
    else:
        print("NO CITATION\n\n")
        print(json_ld.keys())
        print("\n\n")
    return json_ld
