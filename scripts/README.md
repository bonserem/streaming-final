# Scripts

Scripts to configure Kafka or the environment
# Create initial topics
Here are the command to create the topics. For now we have three topics
* raw
 Buffered arrays of measurements.
* clean-latest
  this is a compacted topic containing our own data format. Goals is the latest value per sensor type per box.
  One array per sensor containing the last hour of measurements(mininum 15 instances)
* DEPRECATED clean-all
  contains a time series per box per sensor type
* DEPRECATED raw-history
  since the opensensemap history is in a different format here the raw history data is kept. A separate pipeline converts the history and saves it in the correct topics

here are the commands for creating them:
first connect to one of the brokers

# PM10 topic
contains the latest PM10 measurement per box

```
docker exec -ti kafka-1 bash
```
then create and configure the topics
### raw topic:
```
kafka-topics --zookeeper zookeeper-1:2181 --if-not-exists --create --topic raw --replication-factor 3 --partitions 6 
```
### clean latest topic
```
kafka-topics --zookeeper zookeeper-1:2181 --if-not-exists --create --topic clean-latest --replication-factor 3 --partitions 6 --config cleanup.policy=compact 
```

# Check
Use this command to quickly check if the topics are there:
```
kafka-topics --list --zookeeper zookeeper-1:2181
```
# updating
Here an example command to update a topic
```
kafka-configs --entity-name clean-latest --entity-type topics --zookeeper zookeeper-1:2181 --alter --add-config delete.retention.ms=3600000
```

# Delete
Example to delete a topic and start fresh
```
kafka-topics --delete --topic clean-latest --zookeeper zookeeper-1:2181
```
