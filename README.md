# PySpark SMS Spam Setector

This project implements a fast and scalable SMS spam detection system using PySpark on a Hadoop cluster. With billions of SMS messages sent daily, spam detection is critical to mitigate security threats and financial losses. This solution leverages Apache Spark and Hadoop to efficiently process and classify large volumes of data in a distributed environment.

## Technologies Used
- Apache Spark – in-memory distributed computing

- Hadoop (HDFS + YARN) – scalable storage and resource management

- PySpark – Python API for Spark, enabling seamless integration with Big Data tools

- MLlib – machine learning library in Spark

## How to Deploy on Cluster

### Transfer Files


```bash
scp -r /Users/pyspark-sms-spam-detector/iot-project-backup.zip $linkCluster:/home/sshuser/
```
### On the Cluster
```bash
chmod +x setup.sh
./setup.sh
```

This will:

- Decompress the archive

- Create and activate a virtual environment

- Install required dependencies (PySpark, NumPy, Pandas, etc.)

- Prompt for execution mode (Python or Spark)


### Execution Options
After setup, the script asks:
```bash
How do yo compile the sms-spam-detection?
  1) python3 (normal)
  2) spark-submit
```


It then shows progress via a loading spinner and displays output.txt.


## Notes
Dataset must be located at: src/ds/SMSSpamCollection

The setup step runs only once (tracked by .setup_done)

Tested on HDInsight with Hadoop + Spark

## Inspiration

This project was inspired by the work of **[Junyi (Jerry) Yang](https://github.com/jlyang1990)** in the following repository:  
👉 [Spark_Python_Do_Big_Data_Analytics](https://github.com/jlyang1990/Spark_Python_Do_Big_Data_Analytics)

It builds upon and extends the original ideas for distributed NLP processing with PySpark, adapting them to the **SMS Spam Collection** dataset and focusing on **deployment in Hadoop-based environments** with automation and scalability in mind.
