import pandas as pd
import subprocess
import os
import time

file_name = 'Book1.xlsx'
columns = ['ID hex', 'Rx/Tx', 'Data Length Byte', 'payload']
temp_file_path = "/home/temp/Desktop/python-project/temp.txt"
def read_excel_data(file_name, columns):
    df = pd.read_excel(file_name)
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns {', '.join(missing_columns)}")
    return df[columns].to_dict(orient='records')

def extract_messages(data_list, message_type):
    messages = []
    temp_list = []
    for item in data_list:
        if item['Rx/Tx'] == message_type:
            temp_list.append(item)
        else:
            if temp_list:
                messages.append(temp_list)
                temp_list = []
    if temp_list:
        messages.append(temp_list)
    return messages

def send_can_message(can_id, dlc, payload=""):
    cmd = f'cansend can0 {can_id}#{dlc}{payload}'
    subprocess.run(cmd, shell=True)
    print(f"Sent: {cmd}")

def check_rx_messages(expected_rx):
    for message in expected_rx:
        id_hex = message['ID hex'].strip()
        dlc = message['Data Length Byte'].strip()
        payload = ''.join(str(message["payload"]).split()) if not pd.isna(message["payload"]) else ""
        search_pattern = f"{id_hex}{dlc}{payload}"

        awk_command = f"awk '{{print $6$8$9$10$11$12$13$14$15$16$17$18$19}}' {temp_file_path}"
        grep_command = f"grep {search_pattern}"
        full_command = f"{awk_command} | {grep_command}"
        print(full_command)

        # Continuously try to find the RX message
        while True:
            result = subprocess.run(full_command, shell=True, text=True, capture_output=True)
            if result.returncode == 0:
                print(f"Found RX: {search_pattern}")
                break  # Exit the loop since message is found

    return True  # Return True if all messages are found

def main(file_name, columns):
    try:
        data_list = read_excel_data(file_name, columns)
        tx_data = extract_messages(data_list, 'Tx')
        rx_data = extract_messages(data_list, 'Rx')

        subprocess.Popen(["candump", "-ta", "-x", "can0"], stdout=open(temp_file_path, 'w'))
        for tx_stack, rx_stack in zip(tx_data, rx_data):
            os.system(f"> {temp_file_path}")  # Clear the temporary file before each new TX
            for tx_message in tx_stack:
                send_can_message(str(tx_message["ID hex"]).replace(" ", ""),
                                 str(tx_message["Data Length Byte"]).replace(" ", ""),
                                 str(tx_message["payload"]).replace(" ", "") if not pd.isna(tx_message["payload"]) else "")
            if not check_rx_messages(rx_stack):
                print("Failed to receive all expected RX messages")
        subprocess.run(['pkill', '-f', 'candump'])  # Cleanly kill the candump process

    except Exception as e:
        print(e)

if __name__ == "__main__":
    try:
        main(file_name, columns)
    except Exception as e:
        print(f"Error occurred: {str(e)}")