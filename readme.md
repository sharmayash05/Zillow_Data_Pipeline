# Zillow RapidAPI Data Analytics Project Overview

## Summary
The Zillow RapidAPI Data Analytics project integrates AWS services with Zillow’s API to automate the ingestion, processing, storage, and visualization of property data.

## Technologies
- **AWS Services**: 
  - **S3**: Raw and processed data storage.
  - **EC2**: Runs data processing scripts.
  - **Lambda**: Serverless data ingestion and transformation.
  - **Redshift**: Data warehousing.
  - **QuickSight**: Data visualization.
- **External API**: 
  - **Zillow API (via RapidAPI)**: Retrieves property data.

## Workflow
1. **Data Ingestion**: 
   - Triggered by Airflow DAG; fetches property data from Zillow API.
   - Saves responses in JSON and CSV formats on EC2.
  
2. **Data Storage**: 
   - Moves raw data to S3 in organized folders.

3. **Availability Check**: 
   - S3KeySensor ensures the CSV file is present.

4. **Data Processing**: 
   - Cleans and transforms data on EC2 for Redshift.

5. **Data Warehousing**: 
   - Loads processed data into Redshift.

6. **Data Visualization**: 
   - QuickSight visualizes property trends and metrics.

## Key Components
- **Lambda**: Fetches data and uploads to S3.
- **Python Scripts**: Process data for Redshift.
- **Redshift**: Stores structured property data.
- **QuickSight**: Generates dashboards.

## Future Enhancements
- **Real-Time Updates**: Integrate AWS Step Functions for more frequent data pulls.
- **Additional Sources**: Include other APIs for richer analysis.
- **Machine Learning**: Develop predictive models for property values.

## Challenges and Solutions
- **API Rate Limiting**: Use exponential backoff in Lambda.
- **Large Datasets**: Implement partitioning in Redshift and manage S3 lifecycle.
- **Security**: Ensure least privilege IAM roles.

## Conclusion
This project automates property data extraction from Zillow using AWS services, creating a scalable and efficient analytics pipeline.
