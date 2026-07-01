***

## name: match description: | Compares an unstructured candidate profile with an unstructured job vacancy. Produces an evidence-based assessment of job suitability by identifying Strengths, Gaps, Bonus skills, and an overall Match Level. Use whenever the task involves evaluating a candidate against a vacancy. Do NOT use for CV rewriting, resume generation, interview preparation, or career advice.

# Purpose

Compare a candidate profile and a job vacancy to determine whether the available evidence indicates that the candidate can successfully perform the role.

The analysis is evidence-based, conservative, and independent of vacancy structure.

***

# Inputs

Two plain-text documents:

1. Candidate profile
2. Job vacancy

Both documents are analysed in full.

No preprocessing or structural parsing is required.

***

# Rules

## Evidence only

Use only information explicitly present in the supplied texts.

Never:

* infer missing experience;
* assume unstated skills;
* speculate;
* interpret missing information as negative evidence.

Unknown information remains unknown.

***

## Vacancy understanding

Treat the vacancy as one coherent description.

Identify:

* core responsibilities;
* required competencies;
* technologies;
* expected experience;
* additional desirable skills.

Ignore section names.

***

## Candidate understanding

Treat the profile as one coherent description.

Identify evidence of:

* competencies;
* experience;
* technologies;
* domains;
* project scope;
* additional skills.

***

## Comparison

Evaluate ability to perform the role rather than textual similarity.

The analysis answers:

1. Can the candidate perform the core responsibilities?
2. Which important capabilities are not evidenced?

***

# Definitions

## Strength

Evidence directly supporting successful execution of the core responsibilities.

***

## Gap

Capability, technology or experience required by the role but not evidenced in the profile.

Gap importance depends on impact on job performance, not wording or frequency.

***

## Bonus

Relevant evidence not required by the vacancy but potentially increasing candidate value.

***

# Match Levels

## Strong

Available evidence indicates the candidate can perform the core responsibilities with little or no additional ramp-up.

## Partial

Available evidence indicates the candidate can perform a substantial portion of the role, but several important gaps remain.

## Weak

Available evidence is insufficient to conclude that the candidate can perform the core responsibilities.

***

# Workflow

Perform the following steps internally:

1. Understand the vacancy.
2. Understand the candidate profile.
3. Identify supporting evidence.
4. Identify missing evidence.
5. Determine Match Level.
6. Produce Strength.
7. Produce Gap.
8. Produce Bonus.
9. Produce the required JSON.

Do not expose intermediate reasoning.

***

# Guiding Principle

Ignore formatting differences.

Ignore section ordering.

Ignore keyword frequency.

Always answer one question:

> Based only on the available evidence, can this candidate successfully perform the role described in the vacancy?
