import csv

def export_to_csv(data, filename='ihk_data.csv'):
    keys = data[0].keys() if data else []
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    return filename