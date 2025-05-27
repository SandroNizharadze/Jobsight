import socket

hosts = [
    'aws-0-eu-central-1.pooler.supabase.com',
    'db.mvlceicvjchiqnxpygfm.supabase.co'
]

for host in hosts:
    print(f"Resolving {host}...")
    try:
        # Get IPv4 address
        ip_address = socket.gethostbyname(host)
        print(f"  IPv4: {ip_address}")
        
        # Try to connect to the host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((ip_address, 5432))
        if result == 0:
            print(f"  Connection to {ip_address}:5432 successful")
        else:
            print(f"  Connection to {ip_address}:5432 failed: {result}")
        s.close()
        
    except Exception as e:
        print(f"  Error: {str(e)}") 