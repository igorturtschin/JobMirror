# Concept: Candidate–Vacancy Matching

## Purpose

The system compares two unstructured texts:

* Candidate profile (typically 3,500–7,500 characters, up to 10,000)
* Job vacancy (typically 1,500–2,000 characters)

Both texts are provided to the model in full without prior structuring.

The objective is to determine whether the available evidence indicates that the candidate can successfully perform the role described by the vacancy.

***

## Why Match Percentage Is Not Used

A percentage of matching keywords is not a reliable indicator of suitability because:

* vacancies vary greatly in structure;
* requirement importance is rarely explicit;
* a single requirement may be critical even if mentioned once;
* many minor requirements may occupy most of the text.

The system therefore evaluates job readiness rather than textual similarity.

***

## Vacancy Understanding

The vacancy is treated as one coherent description of the role regardless of section names.

The analysis identifies:

* core responsibilities;
* required competencies;
* technologies;
* expected experience;
* additional desirable skills.

***

## Candidate Understanding

The profile is treated as one coherent description of the candidate.

The analysis identifies evidence of:

* competencies;
* experience;
* technologies;
* domains of expertise;
* project scope;
* additional knowledge and skills.

Only information explicitly stated in the profile is considered evidence.

***

## Evidence-Based Analysis

The analysis relies exclusively on information explicitly present in the profile and vacancy.

It must not:

* infer missing experience;
* assume unstated skills;
* speculate about technologies;
* interpret missing information as negative evidence.

Unknown information remains unknown.

***

## Comparison Principle

The system compares the inferred meaning of both texts rather than individual keywords or sections.

It answers two questions:

1. Can the candidate perform the core responsibilities?
2. Which important capabilities are not evidenced in the profile?

***

## Strength

Evidence from the profile that directly supports successful performance of the core responsibilities.

***

## Gap

A capability, technology or experience required for the role but **not evidenced** in the profile.

A Gap is determined by its impact on performing the job, not by its location or frequency in the vacancy.

***

## Bonus

Evidence in the profile that is not required by the vacancy but could increase the candidate's value.

***

## Match Level

### Strong

The available evidence indicates the candidate can perform the core responsibilities with little or no additional ramp-up.

### Partial

The available evidence indicates the candidate can perform a substantial portion of the role, but several important gaps remain.

### Weak

The available evidence is insufficient to conclude that the candidate can perform the core responsibilities.

***

## Conservative Assessment

When evidence is ambiguous, the analysis prefers the more conservative interpretation.

The system never upgrades a candidate based on assumptions.

***

## Internal Workflow

Before producing the final output, the analysis:

1. Understands the vacancy.
2. Understands the candidate profile.
3. Identifies supporting evidence.
4. Identifies missing evidence.
5. Determines Match Level.
6. Produces Strength.
7. Produces Gap.
8. Produces Bonus.
9. Produces the final JSON.

Intermediate reasoning is never exposed.

***

## Design Principle

The analysis is independent of vacancy structure and never counts matching items.

It always answers the same question:

> **"Based only on the evidence contained in the candidate profile, can this candidate successfully perform the role described in the vacancy?"**
