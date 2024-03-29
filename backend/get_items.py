import json
import logging
import os
import pymysql


rds_host = os.environ.get('DB_HOST')
name = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=3, autocommit=True)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

query = """
SELECT
    i.`id`,
    i.`name`,
    i.`price`,
    i.`taxable`,
    i.`imported`
FROM
    `items` i
"""

def lambda_handler(event, context):
    with conn.cursor() as cur:
        cur.execute(query)
        
        result = cur.fetchall()
        
        items = []
        for row in result:
            items.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'taxable': row[3] == 1,
                'imported': row[4] == 1,
            })

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'data': items,
                'offset': 0,
                'total': len(items),
            })
        }
