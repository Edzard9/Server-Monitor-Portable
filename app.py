import psutil
import GPUtil
import wmi
import pythoncom
import time
from flask import Flask, render_template, jsonify
import socket
import qrcode
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

app = Flask(__name__, template_folder=resource_path('templates'))
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
def get_size(bytes, suffix="GB"):
    factor = 1024 ** 3
    return f"{bytes / factor:.2f}"

def get_all_gpus():
    gpus_data = []
    nvidia_gpus = {}
    try:
        for gpu in GPUtil.getGPUs():
            nvidia_gpus[gpu.name] = gpu
    except:
        pass

    try:
        pythoncom.CoInitialize()
        w = wmi.WMI()
        for video in w.Win32_VideoController():
            gpu_name = video.Name
            load = 0
            mem_total = "N/A"
            mem_used = "N/A"
            display_mem = "N/A"
            
            matched_nvidia = None
            for nv_name, nv_obj in nvidia_gpus.items():
                if nv_name in gpu_name or gpu_name in nv_name:
                    matched_nvidia = nv_obj
                    break
            
            if matched_nvidia:
                load = round(matched_nvidia.load * 100, 1)
                mem_total = round(matched_nvidia.memoryTotal / 1024, 2)
                mem_used = round(matched_nvidia.memoryUsed / 1024, 2)
                display_mem = f"{mem_used} / {mem_total} GB"
            else:
                try:
                    ram_gb = round(int(video.AdapterRAM) / (1024**3), 2)
                    mem_total = ram_gb
                    display_mem = f"{mem_total} GB (Shared)"
                except:
                    display_mem = "Shared Memory"

            gpus_data.append({
                'name': gpu_name,
                'load': load,
                'memory_info': display_mem
            })
    except Exception as e:
        pass

    return gpus_data

def analyze_system_health(ram_percent, disk_percent, boot_time):
    uptime_seconds = time.time() - boot_time
    uptime_days = uptime_seconds / (24 * 3600)
    MAX_UPTIME_DAYS = 15
    days_left = MAX_UPTIME_DAYS - uptime_days
    status = "OPTIMAL"
    message = "Sistem berjalan normal."
    severity = "low"
    if days_left <= 0:
        prediction = "OVERDUE (Segera)"
    else:
        prediction = f"{int(days_left)} Hari Lagi"

    if ram_percent > 90:
        status = "CRITICAL"
        message = "RAM >90%. Risiko crash aplikasi tinggi."
        severity = "high"
        prediction = "SEKARANG"
    elif disk_percent > 95:
        status = "STORAGE FULL"
        message = "Disk sistem penuh. Segera bersihkan cache."
        severity = "high"
    elif days_left <= 0:
        status = "MAINTENANCE"
        message = f"Uptime {int(uptime_days)} hari. Performa mungkin menurun."
        severity = "medium"
    elif ram_percent > 75:
        status = "WARNING"
        message = "Beban RAM tinggi. Monitor ketat."
        severity = "medium"
        prediction = "1-2 Hari (Saran)"
        
    return {
        "status": status, 
        "message": message, 
        "severity": severity,
        "prediction": prediction
    }

#route 
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    cpu_cores = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_usage = round(sum(cpu_cores) / len(cpu_cores), 1) if cpu_cores else 0
    cpu_freq = psutil.cpu_freq()
    curr_freq = round(cpu_freq.current / 1000, 2) if cpu_freq else "N/A"
    logical_cores = psutil.cpu_count(logical=True)

    svmem = psutil.virtual_memory()
    ram_total = get_size(svmem.total)
    ram_usage = svmem.percent

    disks = []
    root_disk_usage = 0
    for part in psutil.disk_partitions():
        try:
            if 'loop' in part.device or part.fstype == '': continue
            usage = psutil.disk_usage(part.mountpoint)
            if part.mountpoint == 'C:\\' or part.mountpoint == '/':
                root_disk_usage = usage.percent
            disks.append({
                'mount': part.mountpoint,
                'total': get_size(usage.total),
                'percent': usage.percent
            })
        except: continue

    gpus = get_all_gpus()

    procs = []
    ignored = ['system idle process', 'system', 'registry', 'idle']
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            with proc.oneshot():
                p = proc.info
                if not p['name']: continue
                if p['name'].lower() in ignored: continue
                if p['cpu_percent'] is None: p['cpu_percent'] = 0
                if p['memory_percent'] is None: p['memory_percent'] = 0
                p['cpu_percent'] = round(p['cpu_percent'] / logical_cores, 1)
                p['memory_percent'] = round(p['memory_percent'], 1)
                procs.append(p)
        except: pass

    top_cpu = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)[:5]
    top_mem = sorted(procs, key=lambda p: p['memory_percent'], reverse=True)[:5]

    boot_time = psutil.boot_time()
    ai_data = analyze_system_health(ram_usage, root_disk_usage, boot_time)

    return jsonify({
        'cpu': {'usage': cpu_usage, 'freq': curr_freq, 'cores': cpu_cores},
        'ram': {'usage': ram_usage, 'total': ram_total},
        'disks': disks,
        'gpus': gpus,
        'top_cpu': top_cpu,
        'top_mem': top_mem,
        'ai': ai_data
    })

#network

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def print_qr_code(url):
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True) 
    print(f"\n[ URL AKSES ] -> {url}")

def find_available_port(start_port):
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1
    raise Exception("Tidak ada port yang tersedia.")

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Mempersiapkan server...")
    ip_address = get_ip_address()
    port = find_available_port(5000)
    full_url = f"http://{ip_address}:{port}"
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*40)
    print("SYSTEM MONITOR SERVER")
    print("="*40)
    print_qr_code(full_url)
    print("\n" + "="*40)
    print(f" STATUS : ONLINE")
    print(f" IP     : {ip_address}")
    print(f" PORT   : {port}")
    print("="*40)
    print(" Tekan CTRL+C untuk menghentikan server.")
    print("="*40 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)