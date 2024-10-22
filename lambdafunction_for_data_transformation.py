import boto3
import json
import pandas as pd

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # TODO implement
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    target_bucket = 'cleaned-data-pro-ec2-csv'
    target_file_name = object_key[:-5]
    print(target_file_name)
   
    waiter = s3_client.get_waiter('object_exists')
    waiter.wait(Bucket=source_bucket, Key=object_key)
    
    response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
    # print(response)
    
    # Read and decode the file content (JSON format)
    file_content = response['Body'].read().decode('utf-8')
    
    # Parse the JSON data
    data = json.loads(file_content)['searchResults']
    # print(data)
    
    # Create an empty list to store the records
    f = []

    # Loop through the searchResults to collect the relevant data
    for result in data:
        property_data = result['property']
        
        # Handle cases where data might be missing using .get() method
        f.append({
            'bathrooms': int(property_data.get('bathrooms', None)),
            'bedrooms': property_data.get('bedrooms', None),
            'city': property_data['address'].get('city', None),
            'listingStatus': property_data['listing'].get('listingStatus', None),
            'propertyType': property_data.get('propertyType', None),
            'livingArea': property_data.get('livingArea', None),
            'price': property_data['price'].get('value', None),
            'rentZestimate': property_data['estimates'].get('rentZestimate', None),
            'zipcode': property_data['address'].get('zipcode', None)
        })

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(f)

    # Select specific columns
    selected_columns = ['bathrooms', 'bedrooms', 'city', 'listingStatus', 
                    'propertyType', 'livingArea', 'price', 'rentZestimate', 'zipcode']

    df = df[selected_columns]

    # Convert DataFrame to CSV format
    csv_data = df.to_csv(index=False)

    # Upload CSV to S3
    s3_client.put_object(Bucket=target_bucket, Key=f"{target_file_name}.csv", Body=csv_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps('CSV conversion and S3 upload completed successfully')
    }

