# Scripts

Scripts to configure Kafka or the environment
# Create initial topics
Here are the command to create the topics. For now we have three topics
* raw
* clean-latest
  this is compacted and kept for an hour
* clean- all

here are the commands for creating them:
first connect to one of the brokers
'''
Docker exec -ti kafka-1 bash
'''
then create and configure the topics
'''
kafka-topics --zookeeper zookeeper-1:2181 --if-not-exists --create --topic clean-latest --replication-factor 3 --partitions 6 --config cleanup.policy=compact delete.retention.ms=3600000

kafka-topics --zookeeper zookeeper-1:2181 --if-not-exists --create --topic raw --replication-factor 3 --partitions 6 --config 

kafka-topics --zookeeper zookeeper-1:2181 --if-not-exists --create --topic clean-all --replication-factor 3 --partitions 6
'''

# Check
Use this command to quickly check if the topics are there:
'''
kafka-topics --list --zookeeper zookeeper-1:2181

# updating


kafka-configs --entity-name clean-latest --entity-type topics --zookeeper zookeeper-1:2181 --alter --add-config delete.retention.ms=3600000


