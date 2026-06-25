#!/usr/bin/env python3
# lab07_ssh_npm.py
# Lab 07: Python SSH Multi-Device Automation

import argparse
import paramiko
import sys
from datetime import datetime

DEFAULT_HOSTS = ['192.168.2.1', '192.168.3.11', '192.168.4.11', '192.168.5.11']
DEFAULT_USER = 'admin'
DEFAULT_PASS = '1234'          
DEFAULT_CMD = 'ip address print'


def run_multi_ssh(hosts, user, pwd, default_cmd='ip address print'):
    """Connect to multiple MikroTik hosts and filter the output to show only its own IP."""
    report_accumulator = []
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    report_accumulator.append("=" * 60)
    report_accumulator.append(f"LAB 07 - MULTI-DEVICE SSH AUTOMATION REPORT")
    report_accumulator.append(f"Execution Time: {timestamp_str}")
    report_accumulator.append("=" * 60 + "\n")

    # Mapping Port Redirection Host Windows ke Target Interface Virtual di MikroTik
    port_mapping = {
        '192.168.2.1': 2222,   
        '192.168.3.11': 2223,  
        '192.168.4.11': 2224,  
        '192.168.5.11': 2225   
    }

    for hostname in hosts:
        command = default_cmd
        host_type = "MikroTik Router"

        header_text = f"SSH to: {hostname} ({host_type}) | Command: {command}"
        print(header_text)
        report_accumulator.append(header_text)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        target_port = port_mapping.get(hostname, 2222)

        try:
            client.connect('127.0.0.1', port=target_port, username=user, password=pwd, timeout=5)
            stdin, stdout, stderr = client.exec_command(command)

            out = stdout.read().decode('utf-8', errors='ignore')
            err = stderr.read().decode('utf-8', errors='ignore')
            
            if out:
                filtered_lines = []
                lines = out.splitlines()
                
                for line in lines:
                    if "Columns:" in line or "#  " in line or "ADDRESS" in line or "Flags:" in line:
                        filtered_lines.append(line)
                    elif hostname in line:
                        filtered_lines.append(line)
                
    
                filtered_output = "\n".join(filtered_lines) + "\n"
                
                print(filtered_output)
                report_accumulator.append(filtered_output)
                
            if err:
                print('STDERR:', err)
                report_accumulator.append(f"STDERR: {err}")

        except Exception as exc:
            err_msg = f"[ERROR] Gagal mengeksekusi SSH ke {hostname}: {exc}"
            print(err_msg, file=sys.stderr)
            report_accumulator.append(err_msg)
            
        finally:
            try:
                client.close()
            except Exception:
                pass
            
            separator = '-' * 50
            print(separator)
            report_accumulator.append(separator + "\n")

    
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"results_{file_timestamp}.txt"
    
    with open(report_filename, "w", encoding="utf-8") as file_log:
        file_log.write("\n".join(report_accumulator))
        
    print(f"\n[SUKSES] Seluruh rangkuman multi-device berhasil dibundel di: '{report_filename}'")


def parse_args():
    parser = argparse.ArgumentParser(description='Multi-host SSH automation script for Lab 07')
    parser.add_argument('-H', '--hosts', nargs='+', default=DEFAULT_HOSTS, help='List of target hosts')
    parser.add_argument('-u', '--user', default=DEFAULT_USER, help='SSH username')
    parser.add_argument('-p', '--password', default=DEFAULT_PASS, help='SSH password')
    parser.add_argument('-c', '--command', default=DEFAULT_CMD, help='Default CLI command')
    return parser.parse_args()


def main():
    args = parse_args()
    run_multi_ssh(args.hosts, args.user, args.password, default_cmd=args.command)


if __name__ == '__main__':
    main()