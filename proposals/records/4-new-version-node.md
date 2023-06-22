# [SomeNewName, the new version of Nuclia's indexing engine]

`nucliadb_node` is the result of implementing the functionality that NucliaDB
has been needing during the early stages of the project. Although the current solution is good enough to
provide the required functionality, the need to mix third party indexes with the ones developed in-house is far from being optimal.\
We are at a point in time where the current implementation is stable and useful enough to give us room to implement the next version. One we 
can control and that can be optimse for Nuclia's needs. 



## Current solution/situation

In `nucliadb_node` one can find the following functionality:

- Grpc API
- Python bindings
- Bm25 and fuzzy search through a Tantivy index
- Fulltext search through a Tantivy index
- Semantic search through `nucliadb_vectors`
- Relations search through `nucliadb_relations`, which uses LMDB.

The main characteristic of this implementation is that `nucliadb_node` uses 4 indexes that are not
related to each other. This means that there is no way of unifying the resources used during a request, the only optimisation 
the node can do, and does, is make the indexes execute the request in parallel. Even though this is an improvement there is no way to 
control the resources that the node uses at a given point in time (file system operations, number of threads, merging of segments, garbage collection, etc..).


## Proposed Solution

[Detailed description of proposed solution]


## Rollout plan

[Describe implementation plan]


## Success Criteria

[How will we know if the proposal was successful?]
