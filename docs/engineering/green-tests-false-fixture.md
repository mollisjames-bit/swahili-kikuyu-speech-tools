# A green test suite can certify a false fixture

*Signal Data Partners engineering note · 30 September 2026*

*Prepared with AI assistance from a local prototype review. The manuscript examples are synthetic; this is not a client case study or a claim of production deployment.*

I would rather return an unresolved-reference queue than a beautifully formatted lie. An AI-generated bibliographic checker made that preference concrete: its local reference table assigned a real PubMed identifier to the wrong paper. Comparing a synthetic manuscript against that table could make invented metadata look verified.

The identifier was PMID 31899120. [PubMed identifies it](https://pubmed.ncbi.nlm.nih.gov/31899120/) as Young Noh, Hong Yup Ahn and In Cheol Hwang’s **Height Loss Is Associated With Suicidal Ideation in Korean Men**, published in 2020, with DOI `10.1016/j.jagp.2019.12.006`. The prototype’s earlier fixture attributed that identifier to a Kenyan health-system paper. This was a source error before it was a Python error.

The tempting response is to add tests. That only helps if the tests obtain their expected answers independently. If the generated fixture supplies both the comparator’s input and the expected result, a passing test says that two copies of the same claim agree. It says nothing about the paper.

## Three different questions hide inside “verified”

For this checker, I separate three questions:

1. Does each input row receive exactly one outcome?
2. Does the submitted metadata agree with the reference snapshot?
3. Was the snapshot checked against an authoritative source?

Row accounting answers the first question. It cannot answer the third. Even a genuine source snapshot does not settle the second if the comparator checks too few fields.

The reviewed comparator checked year, volume and issue when an identifier existed in its local table. Its success branch did not compare the supplied title or DOI. That means correcting the fixture still leaves a failure mode: a row with the correct year, volume and issue but a different title can pass those selected checks. Calling that result an exact match grants the program more authority than its comparisons earn.

Here is a minimal reproduction of that branch and a deliberately narrower replacement. Paste the block into Python 3. It uses a manually checked snapshot and does not make network requests.

```python
from copy import deepcopy

FIELDS = ("title", "year", "volume", "issue", "doi")

def norm(value):
    return " ".join(str(value).split()).casefold()

def old_match(row, snapshot):
    return all(norm(row[k]) == norm(snapshot[k])
               for k in ("year", "volume", "issue"))

def classify(row, snapshots):
    required = ("pmid",) + FIELDS
    if not isinstance(row, dict):
        return "MALFORMED", ("row",)
    missing = tuple(k for k in required
                    if k not in row or row[k] is None
                    or not str(row[k]).strip())
    if missing:
        return "MALFORMED", missing
    source = snapshots.get(str(row["pmid"]))
    if source is None or not source.get("source_url"):
        return "UNRESOLVED", ("source",)
    # A source URL records provenance; it does not authenticate a snapshot.
    if any(k not in source or source[k] is None for k in FIELDS):
        return "UNRESOLVED", ("incomplete_snapshot",)
    differences = tuple(k for k in FIELDS
                        if norm(row[k]) != norm(source[k]))
    return ("DISCREPANCY", differences) if differences else (
        "MATCHES_SELECTED_SNAPSHOT_FIELDS", ())

source = {
    "title": "Height Loss Is Associated With Suicidal Ideation in Korean Men",
    "year": 2020, "volume": "28", "issue": "7",
    "doi": "10.1016/j.jagp.2019.12.006",
    "source_url": "https://pubmed.ncbi.nlm.nih.gov/31899120/",
}
sources = {"31899120": source}
correct = {"pmid": "31899120", **source}
wrong = deepcopy(correct)
wrong["title"] = "Synthetic Kenya health-system study"
wrong["doi"] = "10.example/not-a-real-doi"

assert old_match(wrong, source) is True
assert classify(wrong, sources) == ("DISCREPANCY", ("title", "doi"))
assert classify(correct, sources)[0] == "MATCHES_SELECTED_SNAPSHOT_FIELDS"
unknown = {**correct, "pmid": "not-in-this-snapshot"}
assert classify(unknown, sources)[0] == "UNRESOLVED"
assert classify({**correct, "title": None}, sources)[0] == "MALFORMED"
print("5 checks passed; old comparator accepts the wrong title and DOI.")
```

## Keep the boundary visible

The replacement still is not a complete reference verifier. It does not compare authors, journal or pagination, fetch updates, resolve DOI redirects, validate every field’s type, or decide whether a paper supports an argument. Whitespace folding and case folding are explicit conveniences; they are not fuzzy semantic matching. A punctuation difference becomes a discrepancy for review rather than an automatic correction.

The verbose success label is intentional. `MATCHES_SELECTED_SNAPSHOT_FIELDS` describes the operation. `VERIFIED_ACCURATE` invites someone to read more into it. Likewise, an identifier absent from a small local snapshot is **unresolved**, not nonexistent in PubMed. A lookup failure must not become an accusation that an author invented a source.

For a usable editorial batch, I would add row indexes, the original supplied values, snapshot retrieval time, field differences and source links to the output. Each input row needs one disposition; duplicates should be visible without disappearing or inflating the totals. The proportion of rows matching selected fields should be named exactly that, rather than “accuracy.” Accuracy requires an independent ground truth and a defined evaluation task.

The practical lesson from this review is to test across the source boundary. Check the fixture against the publisher or index, then make a record that has the correct identifier and superficially matching fields but a wrong title. An ordinary happy-path test misses that case. An independently chosen contradiction exposes it immediately.

AI made producing and revising this small checker cheap. Source inspection determined whether its answer deserved to travel beyond the laptop. That distinction is what I want a technical article—and a paid deliverable—to make inspectable.
