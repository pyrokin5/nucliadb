# Sharding and Scaling

This proposal is attempting to synthesize all the ideas around architectural
design for scaling. Most importantly, this proposal details how to leverage
index unification with sharding and shard management strategy to scale NucliaDB
for larger datasets.


## Current solution/situation

Currently, our IndexNode contains our shards. Each shard contains multiple
types of indexes for vector, bm25(with tantivy) and graph capabilities. The implementation
of each index type involves many managed files, threads, etc and can be
quite complex.

Readers and Writers of a shard must be on the same physical machine for a shard.
Right now, that also means a single Kubernetes Pod(part of stateful set).

While we can "rebalance" nodes to some extent, we don't have good metrics
to really know how we should rebalance. Disk size is not a good metric to
know usage of shard.

Moreover, moving a shard is currently tedious. The only implemented option for us
is to reindex a shard on a new shard and cutover the reference of the node the shard is on.
Another option could be to copy all the files; however, this is also slow, error prone,
requires locks and places coupling on the ingest component and our IndexNodes.

Overview of current problems:
- IndexNode is managing multiple types of indexes seperately. High overhead.
- CPU tied to disk and difficult to move shards aroundd
- Reads/writes coupled to disk
- Can not add replicas for an existing KB's shards
- Coupling with shard management and ingest


## Proposed Solution

- Unified index
- Index coordinator
- Shard data
- Shard coordination


### Unified index



#### Breaking changes

- Split from tantivy
- No full entity graph implementation
- No advanced query support

### Replication

- Commit log
- Raft to coordinate replication status between nodes
- 

### Shard Coordinator


Responsibilities:
- Balancing shards across cluster
    - Place new shards appropriate
    - Move shards when things are unbalanced
    - Increase replicas for hot shards
- Record keeping
    - Shard stats
    - Usage stats
- Index queue consuming, operations

APIs:
- Create Shard
- Delete Shard
- Shard Operation
    - Search, etc



## Rollout plan


1. Unified index
2. 


## Success Criteria

[How will we know if the proposal was successful?]
