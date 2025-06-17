#!/usr/bin/env python
# coding: utf-8

"""NLP Project: SMS Spam Detection using Spark
- Uses Spark for dataset management
- Utilizes NLP for text pre-processing (tokenization, stopwords removal)
- Applies TF-IDF for text representation
- Employs Naive Bayes for classification
"""

import os
from pyspark.sql import SparkSession

# Initialize Spark
spark = SparkSession.builder.appName('nlpProject').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")  # Suppress Spark Info Logs

# Load the Dataset (SMS Spam Collection)
dataset_path = os.getenv("DATASET_PATH")
if not dataset_path:
    print("Error: No set for DATASET_PATH.")
    exit(1)

print("\nLoading Dataset...")
data = spark.read.csv(f"file://{dataset_path}", inferSchema=True, sep='\t')
print(f"Dataset Loaded with {data.count()} rows.\n")
data.show(5, truncate=False)

# Renaming Columns for Clarity
print("\nRenaming Columns for Clarity...")
df = data.withColumnRenamed('_c0', 'tag').withColumnRenamed('_c1', 'message')
df.show(5, truncate=False)

# Tokenization: Splitting messages into words
print("\nTokenizing Messages...")
from pyspark.ml.feature import RegexTokenizer
regexTokenizer = RegexTokenizer(inputCol="message", outputCol="words", pattern="\\w+", gaps=False)
df_tokenized = regexTokenizer.transform(df)
df_tokenized.show(5, truncate=False)

# StopWords Removal: Cleaning text data
print("\nRemoving StopWords...")
from pyspark.ml.feature import StopWordsRemover
remover = StopWordsRemover(inputCol='words', outputCol='removed')
df_tokenized_stw = remover.transform(df_tokenized)
df_tokenized_stw.show(5, truncate=False)

# TF-IDF: Text Feature Extraction
print("\nApplying TF-IDF...")
from pyspark.ml.feature import HashingTF, IDF

# Step 1: Term Frequency (TF)
hashing_tf = HashingTF(inputCol='removed', outputCol='rawFeatures')
featurized_data = hashing_tf.transform(df_tokenized_stw)

# Step 2: Inverse Document Frequency (IDF)
idf = IDF(inputCol='rawFeatures', outputCol='features')
idf_model = idf.fit(featurized_data)
rescaled_data = idf_model.transform(featurized_data)
rescaled_data.show(5, truncate=False)

# Label Indexing: Converting 'ham' and 'spam' to binary labels (0 or 1)
print("\nIndexing Labels (ham = 0, spam = 1)...")
from pyspark.ml.feature import StringIndexer
indexer = StringIndexer(inputCol="tag", outputCol="label")
rescaled_data = indexer.fit(rescaled_data).transform(rescaled_data)
rescaled_data.show(5, truncate=False)

# Train/Test Split
print("\nSplitting Data into Train and Test Sets (70% Train, 30% Test)...")
train, test = rescaled_data.randomSplit([0.7, 0.3], seed=42)
print(f"\nTraining Set: {train.count()} rows | Test Set: {test.count()} rows\n")

# Naive Bayes Classification
print("\nTraining Naive Bayes Model...")
from pyspark.ml.classification import NaiveBayes
nb = NaiveBayes(smoothing=1.0, modelType='multinomial', featuresCol='features', labelCol='label')
nb_model = nb.fit(train)

# Model Testing
print("\nTesting Naive Bayes Model...")
test_result = nb_model.transform(test)
test_result.select('label', 'probability', 'prediction').show(10, truncate=False)

# Model Evaluation
print("\nEvaluating Model Performance (F1 Score)...")
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
nb_eval = MulticlassClassificationEvaluator(predictionCol='prediction', labelCol='label', metricName='f1')
f1 = nb_eval.evaluate(test_result)
print(f"\nF1 Score: {f1:.4f}\n")

# Displaying the final result
print("\nSMS Spam Detection Completed Successfully!")
