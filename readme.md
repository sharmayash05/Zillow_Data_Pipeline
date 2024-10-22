# Data Engineering Project: Zillow RapidAPI Data Analytics

## Project Overview
The **data_engineering_project_zillowrapidapi__dataanalytics** focuses on integrating AWS cloud services with external data sources, specifically Zillow’s API via RapidAPI. The project automates data ingestion, processing, storage, and visualization, providing insights into property listings. AWS services like S3, EC2, Lambda, Redshift, and QuickSight are used to create an end-to-end data pipeline.

## Technologies Used
### AWS Services:
- **S3 Bucket**: For data storage (raw and processed data).
- **EC2 Instance**: Running the data processing and API-fetching scripts.
- **AWS Lambda**: For serverless execution of code (data ingestion and transformation).
- **AWS Redshift**: For data warehousing and querying.
- **AWS QuickSight**: For data visualization and analytics.

### External API:
- **Zillow API (via RapidAPI)**: Fetches real estate property data by address.

## Project Workflow
1. **Data Ingestion**:
   - **API Request to Zillow**: The `extract_zillow_data` task in the Airflow DAG initiates a request to Zillow’s API using the endpoint `https://zillow-working-api.p.rapidapi.com/search/byaddress`. Parameters such as `location` and `listingStatus` are passed to obtain detailed property data (including location, price, photos, bedrooms, etc.).
   - **Response Handling**: The API response is received in JSON format. The `extract_zillow_data` function writes this response to both a JSON file and a CSV file on the EC2 instance.
2. **Data Storage**:
   - **Amazon S3**: The raw data fetched via the Zillow API is temporarily stored on the EC2 instance and then moved to an S3 bucket using a BashOperator. The storage structure in S3 can include folders for `/raw/` for unprocessed data and `/processed/` for data ready to be queried or visualized.
3. **Data Availability Check**:
   - **S3KeySensor**: An S3KeySensor checks the availability of the CSV file in the specified S3 bucket. This ensures that the subsequent tasks only execute when the required data is present.
4. **Data Processing**:
   - **EC2 Processing**: A Python script on the EC2 instance processes the raw data. This includes cleaning, transforming, and structuring the data into a format suitable for loading into AWS Redshift.
5. **Data Warehousing**:
   - **AWS Redshift**: The cleaned and transformed data is loaded into AWS Redshift, serving as the centralized data warehouse where various datasets related to properties, locations, pricing trends, etc., are stored.
6. **Data Visualization**:
   - **AWS QuickSight**: Finally, AWS QuickSight is used to visualize the data stored in Redshift. Dashboards created in QuickSight provide insights on property trends, metrics like average property prices by location, price trends over time, and the distribution of properties by the number of bedrooms or bathrooms.

## Key Components
1. ***AWS Lambda Functions***:
   - **Purpose**: Fetch data from Zillow’s API, preprocess it (optional), and upload it to S3.
   - **Lambda Handlers**: Lambda triggers (could be scheduled events) call the function to retrieve new data periodically.
2. ***Python Scripts (EC2)***:
   - `ELT_pipeline_using_airflow.py`: A Python script running on an EC2 instance that further processes the raw data and prepares it for loading into Redshift.
3. ***API Integration***:
   - **Zillow API Endpoint**: The Zillow API provides access to detailed property data. Parameters like `city`, `address`, and `zipcode` are passed to the API, and the response is handled in JSON format.
4. ***Amazon Redshift***:
   - **Data Schema**: Tables for storing property details (e.g., `PropertyDetails`, `PriceHistory`, `MediaLinks`). Each table is related by a unique property identifier (`zpid`).
5. ***Amazon QuickSight***:
   - **Dashboards**: Interactive dashboards visualize key metrics like property distribution, pricing trends, or location-based insights.

## Data Pipeline Architecture
1. ***Triggering Data Ingestion***: 
   - A scheduled Airflow DAG triggers the `extract_zillow_data` task, which makes an API call to Zillow’s endpoint to fetch property data.
   - The task uses parameters such as `location` and `listingStatus` to retrieve the relevant data.
2. ***Extracting Data***: 
   - The `extract_zillow_data` function sends a GET request to the Zillow API with the specified headers and query parameters.
   - The API response, which is in JSON format, is written to a file (both as a JSON and CSV) on the EC2 instance.
3. ***Data Storage***: 
   - After the data is extracted, the output file path is pushed to XCom, allowing subsequent tasks to access the data locations.
   - A BashOperator task moves the JSON file to an S3 bucket for durability and future reference.
4. ***Data Availability Check***: 
   - An S3KeySensor checks if the corresponding CSV file is available in the specified S3 bucket, ensuring that the data is ready for the next step.
5. ***Data Processing***: 
   - A Python script running on an EC2 instance processes the raw data, transforming it into a structured format suitable for Redshift ingestion.
6. ***Data Warehousing***: 
   - The cleaned and transformed data is loaded into AWS Redshift for efficient querying and analytics.
7. ***Data Visualization***: 
   - AWS QuickSight connects to Redshift to visualize the data, providing insights into property trends and facilitating decision-making based on the analytics.

## Future Enhancements
- **Real-Time Data Updates**: Integrate a more frequent data pull mechanism using AWS Step Functions.
- **Additional Data Sources**: Incorporate other APIs or datasets to enhance property analysis, such as crime rates, school ratings, etc.
- **Machine Learning**: Apply predictive models to estimate property values using historical data.

## Challenges and Solutions
- **API Rate Limiting**: Zillow API may impose rate limits. Handle this by implementing exponential backoff in your Lambda functions or using AWS Step Functions for retries.
- **Data Size**: Large datasets from Zillow may lead to slower performance. Use partitioning in Redshift and S3 lifecycle rules to manage old data.
- **Security**: Ensure proper IAM roles for your AWS resources, using least privilege access for S3, Lambda, and Redshift.

## Conclusion
This project automates the extraction of property data using Zillow’s API and provides insightful analytics using AWS cloud services. The use of Lambda, S3, EC2, Redshift, and QuickSight creates a scalable and efficient data pipeline capable of handling large volumes of property data.
