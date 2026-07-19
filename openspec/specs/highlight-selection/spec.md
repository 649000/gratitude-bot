## Purpose

Define the algorithm for selecting which entries appear in digests.

## Requirements

### Requirement: Highlight selection uses a weighted scoring system
The system SHALL score each entry in a digest period using a weighted algorithm:
- Starred entries: +3 points
- Entries longer than 50 characters: +1 point
- Entries containing unique words not present in other top entries: +0.5 points (entity diversity boost)
Entries SHALL be sorted by score descending, and the top N selected for the digest (N depends on cadence: weekly=3-5, monthly=5-8, yearly=8-12).

#### Scenario: Starred entry is prioritized in digest
- **WHEN** generating a weekly digest
- **AND** the user has one starred entry and many unstarred entries in that week
- **THEN** the starred entry appears in the digest with higher priority than unstarred entries of similar length

### Requirement: Entity clustering prevents topic repetition
After scoring, the system SHALL apply entity de-duplication: if multiple top-scoring entries share common significant words (names, places), only the highest-scored entry from each cluster SHALL be included. The next-best entry from a different cluster SHALL replace the removed duplicates.

#### Scenario: Entity clustering removes duplicate topics
- **WHEN** generating a monthly digest
- **AND** 4 of the top 6 entries mention "Sarah"
- **THEN** only the highest-scored Sarah entry is included, replaced by the next-best entries mentioning different topics
