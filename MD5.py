import sys
import hashlib
import json
import platform

def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5()
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
        return md5_hash.hexdigest()

#计算json的md5
def calculate_md5_json(json_data):
    json_str = json.dumps(json_data, sort_keys=False)
    print("The MD5 hash of the JSON data is:", json_str.encode('gbk'))
    md5_hash = hashlib.md5(json_str.encode('gbk'))
    return md5_hash.hexdigest()



if __name__ == "__main__":
    architecture = platform.architecture()[0]
    print(f"The current Python environment is {architecture}.")

    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_path>")
        sys.exit(1)


    file_path = sys.argv[1]
    md5_value = calculate_md5(file_path)

    print(f"MD5 of {file_path} is: {md5_value}")