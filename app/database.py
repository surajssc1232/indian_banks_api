import csv
import requests
import logging
from .models import db, Bank, Branch

logger = logging.getLogger(__name__)

def download_and_load_data():
    try:
        logger.info("Starting data download and loading process...")
        
        csv_url = "https://raw.githubusercontent.com/snarayanank2/indian_banks/master/bank_branches.csv"
        
        logger.info(f"Downloading data from: {csv_url}")
        response = requests.get(csv_url, timeout=60)
        response.raise_for_status()
        
        csv_data = response.text
        csv_reader = csv.DictReader(csv_data.splitlines())
        
        banks_dict = {}
        branches_data = []
        
        logger.info("Processing CSV data...")
        for row in csv_reader:
            bank_name = row['bank_name'].strip()
            
            if bank_name not in banks_dict:
                banks_dict[bank_name] = len(banks_dict) + 1
            
            branch_data = {
                'ifsc': row['ifsc'].strip(),
                'branch': row['branch'].strip() if row['branch'] else '',
                'address': row['address'].strip() if row['address'] else '',
                'city': row['city'].strip() if row['city'] else '',
                'district': row['district'].strip() if row['district'] else '',
                'state': row['state'].strip() if row['state'] else '',
                'bank_name': bank_name
            }
            branches_data.append(branch_data)
        
        logger.info(f"Found {len(banks_dict)} banks and {len(branches_data)} branches")
        
        logger.info("Clearing existing data...")
        Branch.query.delete()
        Bank.query.delete()
        db.session.commit()
        
        logger.info("Inserting banks...")
        bank_objects = []
        for bank_name, bank_id in banks_dict.items():
            bank = Bank(id=bank_id, name=bank_name)
            bank_objects.append(bank)
        
        db.session.bulk_save_objects(bank_objects)
        db.session.commit()
        
        logger.info("Inserting branches...")
        batch_size = 1000
        for i in range(0, len(branches_data), batch_size):
            batch = branches_data[i:i + batch_size]
            branch_objects = []
            
            for branch_data in batch:
                bank_id = banks_dict[branch_data['bank_name']]
                branch = Branch(
                    ifsc=branch_data['ifsc'],
                    branch=branch_data['branch'],
                    address=branch_data['address'],
                    city=branch_data['city'],
                    district=branch_data['district'],
                    state=branch_data['state'],
                    bank_id=bank_id
                )
                branch_objects.append(branch)
            
            db.session.bulk_save_objects(branch_objects)
            db.session.commit()
            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(branches_data)//batch_size) + 1}")
        
        logger.info("Data loading completed successfully!")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download data: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return False

def init_database(app):
    with app.app_context():
        db.create_all()
        
        if Bank.query.first():
            logger.info("Database already contains data. Skipping initialization.")
            return
        
        logger.info("Database is empty. Loading Indian banks data...")
        
        if download_and_load_data():
            logger.info("Successfully loaded real Indian banks data!")
        else:
            logger.warning("Failed to load real data. Using sample data instead.")
            create_sample_data()

def create_sample_data():
    try:
        banks_data = [
            'State Bank of India',
            'HDFC Bank',
            'ICICI Bank',
            'Punjab National Bank',
            'Bank of Baroda'
        ]
        
        bank_objects = []
        for i, bank_name in enumerate(banks_data, 1):
            bank = Bank(id=i, name=bank_name)
            bank_objects.append(bank)
        
        db.session.bulk_save_objects(bank_objects)
        db.session.commit()
        
        sample_branches = [
            {'ifsc': 'SBIN0000001', 'branch': 'New Delhi Main', 'city': 'New Delhi', 'state': 'Delhi', 'bank_id': 1},
            {'ifsc': 'SBIN0000002', 'branch': 'Mumbai Fort', 'city': 'Mumbai', 'state': 'Maharashtra', 'bank_id': 1},
            {'ifsc': 'HDFC0000001', 'branch': 'Bangalore Koramangala', 'city': 'Bangalore', 'state': 'Karnataka', 'bank_id': 2},
            {'ifsc': 'ICIC0000001', 'branch': 'Chennai T Nagar', 'city': 'Chennai', 'state': 'Tamil Nadu', 'bank_id': 3},
            {'ifsc': 'PUNB0000001', 'branch': 'Chandigarh Sector 17', 'city': 'Chandigarh', 'state': 'Punjab', 'bank_id': 4},
        ]
        
        branch_objects = []
        for branch_data in sample_branches:
            branch = Branch(**branch_data)
            branch_objects.append(branch)
        
        db.session.bulk_save_objects(branch_objects)
        db.session.commit()
        
        logger.info("Sample data created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
