---
date: 2023-07-26
status: accepted
---

# Bundle some join-data files


## Context

When we started with the `univention-portal` we extended the CI pipeline so that
the project does provide the join-data file inside of the build artifact
`portal-udm-extensions` and use it from there.

While working on adding the needed LDAP content of other components like UCS or
UDM we faced challenges in working out how to automatically extract the required
data from their sources.


## Decision

For now we "bundle" the join-data files of components when it is difficult to
extract them. This means that we include hand crafted YAML files into the
container image.

The main rationale is that this allows us to focus on providing the required
content faster, so that we have a complete container stack available for the
whole team.


## Consequences

- Good, because we have the container stack available faster.
- Bad, because we duplicate some content and risk running out of sync.
