from netmiko import ConnectHandler

def get_mac_table(ip, username, password):
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }

    net_connect = ConnectHandler(**device)
    output = net_connect.send_command('show mac address-table')
    net_connect.disconnect()

    mac_table = output.split('\n')
    mac_table = [line.split() for line in mac_table if line.strip()]

    return mac_table


def main():
    ip = '192.168.0.99'
    username = 'admin'
    password = 'password'

    mac_table = get_mac_table(ip, username, password)
    print(mac_table)


if __name__ == '__main__':
    main()