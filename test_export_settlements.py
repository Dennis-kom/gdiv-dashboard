from data.static import export_settlements_to_csv
import os

# Export the settlements data to CSV
result = export_settlements_to_csv('settlements_data.csv')

# Show file info
if os.path.exists('settlements_data.csv'):
    print('✓ File created successfully!')
    with open('settlements_data.csv', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        print(f'✓ Total lines: {len(lines)}')
        print('\nFirst 3 lines:')
        for i, line in enumerate(lines[:3]):
            print(f"  Line {i+1}: {line}")
else:
    print('✗ File was not created')

