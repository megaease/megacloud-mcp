from typing import Any, Dict, List, Type
from megacloud_mcp import apis, schema, utils


async def get_monitor_data_of_host_load(tenant_id: int, host: str, start: int, end: int) -> List[Dict]:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-system-load1-avg-metric"},
            {"name": "serverinfo-system-load5-avg-metric"},
            {"name": "serverinfo-system-load15-avg-metric"},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_err_out(tenant_id: int, host: str, start: int, end: int) -> Dict:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-err-out-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_err_in(tenant_id: int, host: str, start: int, end: int) -> Dict:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-err-in-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_disk(tenant_id: int, host: str, start: int, end: int) -> Dict:
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-disk-total-metric", "functions": [{"kind": "max"}], "groups": [{"by": "path.keyword"}]},
            {"name": "serverinfo-disk-used-metric", "functions": [{"kind": "max"}], "groups": [{"by": "path.keyword"}]},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_disk_input_output(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-diskio-read-bytes-ratio-metric"}, {"name": "serverinfo-diskio-write-bytes-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_bytes_sent(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-bytes-sent-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_net_bytes_recv(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [{"name": "serverinfo-net-bytes-recv-ratio-metric"}],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_memory(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-mem-used-avg-metric"},
            {"name": "serverinfo-mem-buffered-avg-metric"},
            {"name": "serverinfo-mem-cached-avg-metric"},
            {"name": "serverinfo-mem-free-avg-metric"},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


async def get_monitor_data_of_host_cpu(tenant_id: int, host: str, start: int, end: int):
    d = {
        "filters": [{"name": "host_name", "values": [host]}],
        "start": start,
        "end": end,
        "metrics": [
            {"name": "serverinfo-cpu-usage-system-avg-metric"},
            {"name": "serverinfo-cpu-usage-user-avg-metric"},
            {"name": "serverinfo-cpu-usage-iowait-avg-metric"},
            {"name": "serverinfo-cpu-usage-idle-avg-metric"},
        ],
    }
    return await apis.get_monitor_data(tenant_id, d)


class MiddlewareMonitorInterface:
    monitor_metrics: Dict[str, Any] = {}

    @classmethod
    def get_monitor_type(cls) -> list[str]:
        return list(cls.monitor_metrics.keys())

    @classmethod
    def get_monitor_metrics(cls, monitor_type: str) -> Any:
        if monitor_type not in cls.monitor_metrics:
            raise ValueError(f"Monitor type {monitor_type} is not supported")
        return cls.monitor_metrics[monitor_type]


class PrometheusMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "TSDBSamplesAppendedTotal": [{"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-head-samples-appended-total-metric"}],
        "ProcessMemoryUsage": [
            {"functions": [{"kind": "max"}], "name": "prometheus-process-resident-memory-bytes-metric"},
            {"functions": [{"kind": "max"}], "name": "prometheus-process-virtual-memory-bytes-metric"},
        ],
        "TSDBWALCorruptionTotal": [{"functions": [{"kind": "max"}], "name": "prometheus-prometheus-tsdb-wal-corruptions-total-metric"}],
        "ActiveTSDBAppendersAndFDs": [
            {"functions": [{"kind": "max"}], "name": "prometheus-prometheus-tsdb-head-active-appenders-metric"},
            {"functions": [{"kind": "max"}], "name": "prometheus-process-open-fds-metric"},
        ],
        "TSDBBlocksLoaded": [{"functions": [{"kind": "max"}], "name": "prometheus-prometheus-tsdb-blocks-loaded-metric"}],
        "TSDBHeadChunks": [{"functions": [{"kind": "max"}], "name": "prometheus-prometheus-tsdb-head-chunks-metric"}],
        "TSDBHeadGCDuration": [
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-head-gc-duration-seconds-sum-metric"},
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-head-gc-duration-seconds-count-metric"},
        ],
        "TSDBCompactionStats": [
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-compactions-total-metric"},
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-compactions-failed-total-metric"},
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-compactions-triggered-total-metric"},
        ],
        "TSDBReloadsTotal": [{"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-tsdb-reloads-total-metric"}],
        "EngineQueryDurationRatios": [
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-engine-query-duration-seconds-sum-ratio-metric"},
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-engine-query-duration-seconds-count-ratio-metric"},
        ],
        "RuleGroupEvaluationDuration": [
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-rule-group-duration-seconds-sum-metric"},
            {"functions": [{"kind": "increment"}], "name": "prometheus-prometheus-rule-group-duration-seconds-count-metric"},
        ],
        "ServiceDiscoveryAndCacheErrors": [
            {"name": "prometheus-prometheus-sd-consul-rpc-failures-total-ratio-metric"},
            {"name": "prometheus-prometheus-sd-dns-lookup-failures-total-ratio-metric"},
            {"name": "prometheus-prometheus-treecache-zookeeper-failures-total-ratio-metric"},
            {"name": "prometheus-prometheus-tsdb-head-series-not-found-total-ratio-metric"},
        ],
        "TSDBHeadSeriesStats": [
            {"name": "prometheus-prometheus-tsdb-head-series-max-metric"},
            {"name": "prometheus-prometheus-tsdb-head-series-created-total-ratio-metric"},
            {"name": "prometheus-prometheus-tsdb-head-series-removed-total-ratio-metric"},
        ],
        "TargetScrapePoolSyncEvents": [{"name": "prometheus-prometheus-target-scrape-pool-sync-total-ratio-metric"}],
    }


class MySQLMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "SlowQueryRatio": [{"name": "mysql-slow-queries-ratio-metric"}],
        "CommandTypeRatios": [
            {"name": "mysql-com-insert-ratio-metric"},
            {"name": "mysql-com-select-ratio-metric"},
            {"name": "mysql-com-update-ratio-metric"},
            {"name": "mysql-com-update-multi-ratio-metric"},
            {"name": "mysql-com-delete-ratio-metric"},
            {"name": "mysql-com-delete-multi-ratio-metric"},
            {"name": "mysql-com-insert-select-ratio-metric"},
            {"name": "mysql-com-replace-ratio-metric"},
            {"name": "mysql-com-replace-select-ratio-metric"},
            {"name": "mysql-com-commit-ratio-metric"},
            {"name": "mysql-com-rollback-ratio-metric"},
            {"name": "mysql-com-stmt-execute-ratio-metric"},
            {"name": "mysql-com-call-procedure-ratio-metric"},
        ],
        "InnoDBRowOpsRatios": [
            {"name": "mysql-innodb-rows-read-ratio-metric"},
            {"name": "mysql-innodb-rows-deleted-ratio-metric"},
            {"name": "mysql-innodb-rows-inserted-ratio-metric"},
            {"name": "mysql-innodb-rows-updated-ratio-metric"},
        ],
        "InnoDBIOActivity": [{"name": "mysql-innodb-data-reads-ratio-metric"}, {"name": "mysql-innodb-data-writes-ratio-metric"}],
        "AbortedAndLockedConnectionRatios": [{"name": "mysql-aborted-connects-ratio-metric"}, {"name": "mysql-locked-connects-ratio-metric"}],
        "ThreadAndConnectionCounts": [{"name": "mysql-threads-running-sum-metric"}, {"name": "mysql-threads-connected-sum-metric"}],
        "StorageUsageSummary": [
            {"name": "mysql-table-schema-data-length-sum-metric"},
            {"name": "mysql-table-schema-index-length-sum-metric"},
            {"name": "mysql-binary-size-bytes-sum-metric"},
        ],
        "OSLogFsyncRatio": [{"name": "mysql-os-log-fsyncs-ratio-metric"}],
        "NetworkThroughputRatios": [{"name": "mysql-bytes-received-ratio-metric"}, {"name": "mysql-bytes-sent-ratio-metric"}],
    }


class KafkaMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "TopicPartitionOffsetRatio": [{"name": "kafka-topic-offset-offset-ratio-metric"}],
        "ConsumerGroupMaxLag": [{"name": "kafka-group-topic-total-lag-max-by-group-metric"}],
        "ConsumerGroupMaxPartitionCount": [{"name": "kafka-group-topic-partition-count-max-by-group-metric"}],
        "TopicMessagesInPerSec1m": [{"name": "kafka-topics-messagesinpersec-oneminuterate-max-metric"}],
        "TopicBytesInPerSec1m": [{"name": "kafka-topics-bytesinpersec-oneminuterate-max-metric"}],
        "TopicBytesOutPerSec1m": [{"name": "kafka-topics-bytesoutpersec-oneminuterate-max-metric"}],
        "HostProduceRequestsPerSecRatio": [
            {"name": "kafka-topics-totalproducerequestspersec-count-ratio-metric", "groups": [{"by": "host_name"}]},
            {"name": "kafka-topics-failedproducerequestspersec-count-ratio-metric", "groups": [{"by": "host_name"}]},
        ],
        "HostProduceMessageConversionsPerSecRatio": [
            {"name": "kafka-topics-producemessageconversionspersec-count-ratio-metric", "groups": [{"by": "host_name"}]}
        ],
        "UnderReplicatedPartitions": [{"name": "kafka-replica-manager-underreplicatedpartitions-value-max-metric"}],
        "OfflineReplicaCount": [{"name": "kafka-replica-manager-offlinereplicacount-value-max-metric"}],
        "LeaderCount": [{"name": "kafka-replica-manager-leadercount-value-max-metric"}],
        "PartitionCount": [{"name": "kafka-replica-manager-partitioncount-value-max-metric"}],
        "ControllerLeaderElectionRateAndTimeMs": [{"name": "kafka-controller-leaderelectionrateandtimems-max-max-metric"}],
        "UncleanLeaderElectionsPerSec": [{"name": "kafka-controller-uncleanleaderelectionspersec-oneminuterate-max-metric"}],
        "ActiveControllerCount": [{"name": "kafka-controller-activecontrollercount-value-max-metric"}],
        "GlobalTopicCount": [{"name": "kafka-controller-globaltopiccount-value-max-metric"}],
        "GlobalPartitionCount": [{"name": "kafka-controller-globalpartitioncount-value-max-metric"}],
        "JavaCpuUseParSecond": [
            {"name": "kafka-process-cpu-seconds-total-ratio-metric", "groups": [{"by": "devicename"}], "functions": [{"kind": "increment"}]}
        ],
        "JavaMemoryPool": [{"name": "kafka-java-memory-pool-usage-used-max-by-tag-name-metric"}],
        "JavaThreadPool": [
            {"name": "kafka-java-threading-daemonthreadcount-max-metric"},
            {"name": "kafka-java-threading-threadcount-max-metric"},
            {"name": "kafka-java-threading-peakthreadcount-max-metric"},
        ],
        "JavaGCCount": [{"name": "kafka-java-garbage-collector-collectioncount-ratio-metric"}],
        "JavaGCTime": [{"name": "kafka-java-garbage-collector-collectiontime-ratio-metric"}],
    }


class RedisMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "KeyspaceKeys": [{"name": "redis-keyspace-keys-metric", "groups": [{"by": "database.keyword"}], "functions": [{"kind": "max"}]}],
        "MemoryUsage": [
            {"name": "redis-used-memory-metric", "functions": [{"kind": "max"}]},
            {"name": "redis-used-memory-rss-metric", "functions": [{"kind": "max"}]},
        ],
        "KeyspaceHitsMisses": [
            {"name": "redis-keyspace-hits-metric", "functions": [{"kind": "increment"}]},
            {"name": "redis-keyspace-misses-metric", "functions": [{"kind": "increment"}]},
        ],
        "KeysEvictedExpired": [
            {"name": "redis-evicted-keys-metric", "functions": [{"kind": "increment"}]},
            {"name": "redis-expired-keys-metric", "functions": [{"kind": "increment"}]},
        ],
        "ClientConnections": [
            {"name": "redis-clients-metric", "functions": [{"kind": "max"}]},
            {"name": "redis-blocked-clients-metric", "functions": [{"kind": "max"}]},
        ],
        "InstantaneousOpsPerSec": [{"name": "redis-instantaneous-ops-per-sec-metric", "functions": [{"kind": "max"}, {"kind": "min"}, {"kind": "avg"}]}],
        "KeyspaceHitRate": [{"name": "redis-keyspace-hitrate-metric", "functions": [{"kind": "min"}]}],
        "MemoryFragmentationRatio": [{"name": "redis-mem-fragmentation-ratio-metric", "functions": [{"kind": "min"}]}],
        "TotalCommandsProcessed": [{"name": "redis-total-commands-processed-metric", "functions": [{"kind": "increment"}]}],
        "ConnectionsStats": [{"name": "redis-total-connections-received-metric"}, {"name": "redis-rejected-connections-metric"}],
        "NetworkThroughput": [{"name": "redis-net-input-throughput-bytes-metric"}, {"name": "redis-net-output-throughput-bytes-metric"}],
        "ConnectedReplicas": [{"name": "redis-connected-slaves-metric", "functions": [{"kind": "max"}]}],
    }


class NginxMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "ConnectionStates": [
            {"name": "nginx-vts-connections-reading-metric"},
            {"name": "nginx-vts-connections-writing-metric"},
            {"name": "nginx-vts-connections-waiting-metric"},
            {"name": "nginx-vts-connections-active-metric"},
        ],
        "ResponseStatusRatios": [
            {"name": "nginx-vts-server-response-2xx-count-ratio-metric"},
            {"name": "nginx-vts-server-response-4xx-count-ratio-metric"},
            {"name": "nginx-vts-server-response-5xx-count-ratio-metric"},
        ],
        "RequestStats": [
            {"name": "nginx-vts-server-request-time-ratio-metric"},
            {"name": "nginx-vts-server-requests-ratio-metric"},
        ],
        "ServerTraffic": [
            {"name": "nginx-vts-server-in-bytes-ratio-metric"},
            {"name": "nginx-vts-server-out-bytes-ratio-metric"},
        ],
        "UpstreamTraffic": [
            {"name": "nginx-vts-upstream-in-bytes-ratio-metric"},
            {"name": "nginx-vts-upstream-out-bytes-ratio-metric"},
        ],
        "CacheStats": [
            {"name": "nginx-vts-server-cache-bypass-sum-metric"},
            {"name": "nginx-vts-server-cache-expired-sum-metric"},
            {"name": "nginx-vts-server-cache-hit-sum-metric"},
            {"name": "nginx-vts-server-cache-miss-sum-metric"},
            {"name": "nginx-vts-server-cache-revalidated-sum-metric"},
            {"name": "nginx-vts-server-cache-scarce-sum-metric"},
            {"name": "nginx-vts-server-cache-stale-sum-metric"},
            {"name": "nginx-vts-server-cache-updating-sum-metric"},
        ],
    }


class PostgreSQLMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "NumBackendsMax": [
            {
                "name": "postgresql-numbackends-max-by-postgresql-datname-metric",
            },
        ],
        "XactCommitRollbackRate": [
            {
                "name": "postgresql-xact-commit-ratio-metric",
            },
            {
                "name": "postgresql-xact-rollback-ratio-metric",
            },
        ],
        "RowsQueryRate": [
            {
                "name": "postgresql-tup-returned-ratio-metric",
            },
            {
                "name": "postgresql-tup-fetched-ratio-metric",
            },
        ],
        "RowsModifyRate": [
            {
                "name": "postgresql-tup-inserted-ratio-metric",
            },
            {
                "name": "postgresql-tup-updated-ratio-metric",
            },
            {
                "name": "postgresql-tup-deleted-ratio-metric",
            },
        ],
        "TempFilesInfoRate": [
            {
                "name": "postgresql-temp-files-ratio-metric",
            },
            {
                "name": "postgresql-temp-bytes-ratio-metric",
            },
        ],
        "DeadlocksRate": [
            {
                "name": "postgresql-deadlocks-ratio-metric",
            },
        ],
    }


class ElasticSearchMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "HttpTotalOpenedRatio": [
            {
                "name": "elasticsearch-http-total-opened-ratio-metric",
            },
        ],
        "IndicesSearchQueryCount": [
            {
                "name": "elasticsearch-indices-search-query-total-ratio-metric",
            },
            {
                "name": "elasticsearch-indices-search-fetch-total-ratio-metric",
            },
        ],
        "IndicesSearchQueryTimeMillis": [
            {
                "name": "elasticsearch-indices-search-query-time-in-millis-ratio-metric",
            },
            {
                "name": "elasticsearch-indices-search-fetch-time-in-millis-ratio-metric",
            },
        ],
        "JvmMemoryUsedBytes": [
            {
                "name": "elasticsearch-jvm-mem-heap-used-in-bytes-sum-metric",
            },
            {
                "name": "elasticsearch-jvm-mem-non-heap-used-in-bytes-sum-metric",
            },
            {
                "name": "elasticsearch-jvm-mem-pools-old-used-in-bytes-sum-metric",
            },
            {
                "name": "elasticsearch-jvm-mem-pools-survivor-used-in-bytes-sum-metric",
            },
            {
                "name": "elasticsearch-jvm-mem-pools-young-used-in-bytes-sum-metric",
            },
        ],
        "JvmGcCollectionCountRate": [
            {
                "name": "elasticsearch-jvm-gc-collectors-young-collection-count-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
            {
                "name": "elasticsearch-jvm-gc-collectors-old-collection-count-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
        ],
        "JvmGcCollectionTimeMillisRate": [
            {
                "name": "elasticsearch-jvm-gc-collectors-young-collection-time-in-millis-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
            {
                "name": "elasticsearch-jvm-gc-collectors-old-collection-time-in-millis-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
        ],
        "IndicesTranslogOperations": [
            {
                "name": "elasticsearch-indices-translog-operations-metric",
                "functions": [
                    {
                        "kind": "max",
                    },
                ],
            },
        ],
        "IndicesTranslogSizeBytes": [
            {
                "name": "elasticsearch-indices-translog-size-in-bytes-metric",
                "functions": [
                    {
                        "kind": "max",
                    },
                ],
            },
        ],
        "IndicesDocsCount": [
            {
                "name": "elasticsearch-indices-docs-count-metric",
                "functions": [
                    {
                        "kind": "max",
                    },
                ],
            },
        ],
        "IndicesDocsIndexedRate": [
            {
                "name": "elasticsearch-indices-indexing-index-total-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
        ],
        "IndicesDocsDeletedRate": [
            {
                "name": "elasticsearch-indices-docs-deleted-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
        ],
        "IndicesMergesTotalRate": [
            {
                "name": "elasticsearch-indices-merges-total-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
        ],
        "IndicesMergesTotalSizeBytes": [
            {
                "name": "elasticsearch-indices-merges-total-size-in-bytes-metric",
                "functions": [
                    {
                        "kind": "increment",
                    },
                ],
            },
        ],
    }


class DockerMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "CpuUsagePercent": [
            {
                "name": "docker-cpu-usage-percent-max-by-container-name-metric",
            },
        ],
        "MemoryUsage": [
            {"name": "docker-mem-usage-max-by-container-name-metric"},
            {"name": "docker-mem-rss-max-by-container-name-metric"},
            {"name": "docker-mem-cache-max-by-container-name-metric"},
        ],
        "NetworkBytesRatio": [
            {"name": "docker-net-rx-bytes-ratio-metric"},
            {"name": "docker-net-tx-bytes-ratio-metric"},
        ],
        "DiskIoBytesRatio": [
            {
                "name": "docker-blkio-io-service-bytes-recursive-read-ratio-metric",
            },
            {
                "name": "docker-blkio-io-service-bytes-recursive-write-ratio-metric",
            },
        ],
        "UsedFileDescriptors": [
            {
                "functions": [{"kind": "avg"}],
                "name": "docker-n-used-file-descriptors-metric",
            },
        ],
        "ContainersCount": [
            {
                "functions": [{"kind": "avg"}],
                "name": "docker-n-containers-metric",
            },
            {
                "functions": [{"kind": "avg"}],
                "name": "docker-n-containers-running-metric",
            },
            {
                "functions": [{"kind": "avg"}],
                "name": "docker-n-containers-stopped-metric",
            },
            {
                "functions": [{"kind": "avg"}],
                "name": "docker-n-containers-paused-metric",
            },
        ],
        "ImagesCount": [
            {
                "functions": [{"kind": "avg"}],
                "name": "docker-n-images-metric",
            },
        ],
    }


class MinIOMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "BucketUsageObjectCount": [
            {
                "name": "minio-bucket-usage-object-total-max-by-bucket-metric",
            },
        ],
        "BucketUsageTotalBytes": [
            {
                "name": "minio-bucket-usage-total-bytes-max-by-bucket-metric",
            },
        ],
        "ClusterNodesCount": [
            {
                "name": "minio-cluster-nodes-offline-total-max-metric",
            },
            {
                "name": "minio-cluster-nodes-online-total-max-metric",
            },
        ],
        "ClusterDisksCount": [
            {
                "name": "minio-cluster-disk-offline-total-max-metric",
            },
            {
                "name": "minio-cluster-disk-online-total-max-metric",
            },
        ],
        "ClusterCapacityUsableBytes": [
            {
                "name": "minio-cluster-capacity-usable-free-bytes-max-metric",
            },
            {
                "name": "minio-cluster-capacity-usable-total-bytes-max-metric",
            },
        ],
        "NodeDiskFreeBytes": [
            {
                "name": "minio-node-disk-free-bytes-max-by-disk-metric",
            },
        ],
        "S3TrafficReceivedBytes": [
            {
                "name": "minio-s3-traffic-received-bytes-max-metric",
            },
        ],
        "S3TrafficSentBytes": [
            {
                "name": "minio-s3-traffic-sent-bytes-max-metric",
            },
        ],
        "NodeMemoryUsedBytes": [
            {
                "name": "minio-node-process-resident-memory-bytes-max-metric",
            },
        ],
        "NodeCpuTimeRatio": [
            {
                "name": "minio-node-process-cpu-total-seconds-ratio-metric",
            },
        ],
    }


class MongoDBMonitor(MiddlewareMonitorInterface):
    monitor_metrics = {
        "CurrentConnections": [
            {"name": "mongodb-connections-current-sum-metric"},
        ],
        "CommandThroughputRate": [
            {
                "name": "mongodb-find-command-total-ratio-metric",
            },
            {
                "name": "mongodb-find-and-modify-command-total-ratio-metric",
            },
            {
                "name": "mongodb-distinct-command-total-ratio-metric",
            },
            {
                "name": "mongodb-count-command-total-ratio-metric",
            },
            {
                "name": "mongodb-delete-command-total-ratio-metric",
            },
            {
                "name": "mongodb-get-more-command-total-ratio-metric",
            },
            {
                "name": "mongodb-insert-command-total-ratio-metric",
            },
            {
                "name": "mongodb-update-command-total-ratio-metric",
            },
            {
                "name": "mongodb-aggregate-command-total-ratio-metric",
            },
        ],
        "LatencyRate": [
            {"name": "mongodb-latency-reads-count-ratio-metric"},
            {"name": "mongodb-latency-writes-count-ratio-metric"},
            {"name": "mongodb-latency-reads-ratio-metric"},
            {"name": "mongodb-latency-writes-ratio-metric"},
        ],
        "ReplLagCardinality": [
            {"name": "mongodb-repl-lag-cardinality-metric"},
        ],
        "CursorCount": [
            {
                "name": "mongodb-cursor-total-count-max-metric",
            },
            {
                "name": "mongodb-cursor-pinned-count-max-metric",
            },
            {
                "name": "mongodb-cursor-timed-out-count-max-metric",
            },
            {
                "name": "mongodb-cursor-no-timeout-count-max-metric",
            },
        ],
        "DocumentOpRate": [
            {
                "name": "mongodb-document-deleted-ratio-metric",
            },
            {
                "name": "mongodb-document-inserted-ratio-metric",
            },
            {
                "name": "mongodb-document-returned-ratio-metric",
            },
            {
                "name": "mongodb-document-updated-ratio-metric",
            },
        ],
        "NetInBytesRate": [
            {
                "name": "mongodb-net-in-bytes-count-ratio-metric",
            },
            {
                "name": "mongodb-net-in-bytes-count-ratio-metric",
            },
        ],
        "QueuedRequestsCount": [
            {"name": "mongodb-queued-reads-sum-metric"},
            {"name": "mongodb-queued-writes-sum-metric"},
        ],
        "ResidentMemoryMB": [
            {
                "name": "mongodb-resident-megabytes-max-metric",
            },
        ],
        "PageFaultsMax": [
            {
                "name": "mongodb-page-faults-max-metric",
            },
        ],
        "DataSizeMax": [
            {
                "name": "mongodb-data-size-max-metric",
            },
        ],
    }


MIDDLEWARE_MONITOR_MAP: Dict[str, Type[MiddlewareMonitorInterface]] = {
    "prometheus": PrometheusMonitor,
    "mysql": MySQLMonitor,
    "kafka": KafkaMonitor,
    "redis": RedisMonitor,
    "nginx": NginxMonitor,
    "postgresql": PostgreSQLMonitor,
    "elasticsearch": ElasticSearchMonitor,
    "docker": DockerMonitor,
    "minio": MinIOMonitor,
    "mongodb": MongoDBMonitor,
}


async def get_middleware_monitor_metrics(middleware_instance_name: str) -> List[str]:
    instance = await apis.get_middleware_instance(middleware_instance_name)
    middleware_name = instance.middleware_name.lower()
    if middleware_name not in MIDDLEWARE_MONITOR_MAP:
        raise ValueError(f"Middleware {middleware_name} is not supported")
    middleware_monitor = MIDDLEWARE_MONITOR_MAP[middleware_name]
    return middleware_monitor.get_monitor_type()


async def get_monitor_metrics(middleware_instance_name: str, monitor_type: str) -> Any:
    instance = await apis.get_middleware_instance(middleware_instance_name)
    middleware_name = instance.middleware_name.lower()
    if middleware_name not in MIDDLEWARE_MONITOR_MAP:
        raise ValueError(f"Middleware {middleware_name} is not supported")
    middleware_monitor = MIDDLEWARE_MONITOR_MAP[middleware_name]
    return middleware_monitor.get_monitor_metrics(monitor_type)


async def get_middleware_monitor_data(arg: schema.MiddlewareInstanceMonitorDataSchema) -> Dict:
    tenant_id = await apis.get_tenant_id()
    start, end = utils.get_start_end_time(arg.time_interval_in_minutes)
    d = {
        "filters": [{"name": "service", "values": [arg.middleware_instance_name]}, {"name": "node_name", "values": [arg.node_name]}],
        "start": start,
        "end": end,
        "metrics": await get_monitor_metrics(arg.middleware_instance_name, arg.metric_name),
    }
    return await apis.get_monitor_data(tenant_id, d)
