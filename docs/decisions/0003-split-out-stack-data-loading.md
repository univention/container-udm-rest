---
date: 2023-08-15
status: accepted
consulted: TODO
---

# Split out loading of the stack data


## Context

We did start to load the initial data as part of this repository with a small
Kubernetes Job. Initially this was only the data related to the
`univention-portal`, now this does also contain data related to various other
components like UDM or UMC. As a next step we want to add even further data
which shall be loaded into a stack deployment.

Now we have this repository which deals with two different things:

- Providing the UDM Rest API as a container and a Helm chart for Kubernetes
  deployment.

- Loading of data into a deployment of the UMS Stack.


## Decision

We split out the aspect of loading data into the UMS Stack into a separate
repository.

The main rationale is that this way this repository will stay focused on
providing the UDM Rest API in a container. The regular expansion in needs of
data to be loaded or related tooling to be improved would clutter this
repository.

Also the aspect of loading initial data into the stack would be in a repository
with a very narrow scope.


## Consequences

- Good, because this repository would have a clear focus.
- Good, because the data loading would also be in a focused repository.
- Good, setting up automatic versioning and releasing for the repositories is
  easier.
- Bad, a little bit of work to refactor the setup is needed.
