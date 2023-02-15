import csv
import sys

# Check if the script was called with a filename argument
if len(sys.argv) != 2:
    print("Usage: python change_delimiter.py <filename>")
    sys.exit(1)

# Open the input file and read the data
input_file = sys.argv[1]
with open(input_file, newline='') as f:
    reader = csv.reader(f)
    data = [row for row in reader]

# Change the delimiter from commas to semicolons
for i in range(len(data)):
    data[i] = ';'.join(data[i])

# Open the output file and write the new data
output_file = input_file.replace('.csv', '_new.csv')
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f"File saved as {output_file}")
