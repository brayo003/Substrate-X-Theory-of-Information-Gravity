# This script will fix the method call issue
import fileinput
import sys

# Read the current file
with open('universal_dynamics_engine/predictive_engine.py', 'r') as f:
    content = f.read()

# Fix the method calls - replace the problematic section
old_code = '''        # Process and inject data
        finance_metrics = self.data_coupler.ingest_data(
            financial_data, DomainType.FINANCIAL
        ).output_metrics()
        
        bio_metrics = self.data_coupler.ingest_data(
            biological_data, DomainType.BIOLOGICAL  
        ).output_metrics()'''

new_code = '''        # Process and inject data - FIXED
        financial_coupler = DataCoupler(domain_type=DomainType.FINANCIAL)
        finance_metrics = financial_coupler.ingest_data(financial_data).output_metrics()
        
        bio_coupler = DataCoupler(domain_type=DomainType.BIOLOGICAL)
        bio_metrics = bio_coupler.ingest_data(biological_data).output_metrics()'''

# Replace the code
content = content.replace(old_code, new_code)

# Write back
with open('universal_dynamics_engine/predictive_engine.py', 'w') as f:
    f.write(content)

print("✅ Fixed the DataCoupler method calls")
