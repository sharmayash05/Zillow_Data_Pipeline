# import the libraries
import json
import requests
from datetime import timedelta , datetime
from airflow.utils.dates import days_ago

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; you need this to write tasks!
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

with open('/home/ubuntu/airflow/dags/config_api.json') as congif_file:
    api_host_key=json.load(congif_file)

now = datetime.now()
dt_now_string = now.strftime('%d%m%Y%H%M%S')

#Function to extract zillow data

def extract_zillow_data(**kwargs):
    url = kwargs['url']
    headers = kwargs['headers']
    querystring = kwargs['querystring']
    dt_string = kwargs['date_string']
    # return headers
    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()
    

    # Specify the output file path
    output_file_path = f"/home/ubuntu/response_data_{dt_string}.json"
    file_str = f'response_data_{dt_string}.csv'

    # Write the JSON response to a file
    with open(output_file_path, "w") as output_file:
        json.dump(response_data, output_file, indent=4)  # indent for pretty formatting

      # Push the output to XCom
    kwargs['ti'].xcom_push(key='extract_zillow_data_var', value=[output_file_path, file_str])  # Ensure this is a list

    output_list = [output_file_path, file_str]
    return output_list

#defining DAG arguments
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(0),
    'email': ['123@gmail.com'],
    'email_on_failure':False,
    'email_on_retry':False,
    'retries': 2,
    'retry_delay': timedelta(seconds=5),
}

# defining the DAG

# define the DAG
dag = DAG(
    'zillow_pro_ec2_dag',
    default_args=default_args,
    description='Zillow Data Analytics',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# define the tasks
# define the first task

extract_zillow_data_var = PythonOperator(
    task_id='extract_zillow_data',
    python_callable=extract_zillow_data,
    op_kwargs={'url': "https://zillow-working-api.p.rapidapi.com/search/byaddress",  'querystring': {"location":"houston, tx","listingStatus":"For_Sale"}, 'headers': api_host_key, 'date_string':dt_now_string},
    provide_context=True,
    dag=dag,
)

# define the second task
load_data_to_s3 = BashOperator(
    task_id='load_data_to_s3',
    bash_command='aws s3 mv {{ ti.xcom_pull(task_ids="extract_zillow_data", key="extract_zillow_data_var")[0] }} s3://project-ec2-raw-data/',
    dag=dag,
)


# define the third task
is_csv_clean_data_available = S3KeySensor(
      task_id='is_csv_clean_data_available',
        bucket_key='{{ ti.xcom_pull(task_ids="extract_zillow_data", key="extract_zillow_data_var")[1] }}',
        bucket_name='cleaned-data-pro-ec2-csv',
        aws_conn_id='aws_s3_conn',
        wildcard_match=False,  # Set this to True if you want to use wildcards in the prefix
        timeout=60,  # Optional: Timeout for the sensor (in seconds)
        poke_interval=5,  # Optional: Time interval between S3 checks (in seconds)
        dag=dag,
)

# define the fourth task

transfer_data_s3_to_redshift = S3ToRedshiftOperator(
    task_id="transfer_s3_to_redshift",
    aws_conn_id='aws_s3_conn',
    redshift_conn_id='conn_id_redshift',
    s3_bucket='cleaned-data-pro-ec2-csv',
    s3_key='{{ ti.xcom_pull(task_ids="extract_zillow_data", key="extract_zillow_data_var")[1] }}',
    schema="PUBLIC",
    table="pro_ec2_data",
    copy_options=["csv IGNOREHEADER 1"],
    dag=dag,
)


# task pipeline
extract_zillow_data_var >> load_data_to_s3 >> is_csv_clean_data_available >> transfer_data_s3_to_redshift
