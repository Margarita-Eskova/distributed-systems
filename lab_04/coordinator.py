import requests
import ssl
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Список серверов
SERVERS = [
    {"port": 5001, "url": "https://localhost:5001/data", "active": True},
    {"port": 5002, "url": "https://localhost:5002/data", "active": True}
]

CA_CERT = "certs/ca_cert.pem"
CLIENT_CERT = "certs/client_cert.pem"
CLIENT_KEY = "certs/client_key.pem"

# Сертификаты для САМОГО координатора (чтобы клиент мог подключиться)
COORD_CERT = "certs/server_cert.pem"
COORD_KEY = "certs/server_key.pem"

def get_active_server():
    for server in SERVERS:
        if server["active"]:
            return server
    return None

def check_server_health(server):
    try:
        metrics_url = f"https://localhost:{server['port']}/metrics"
        resp = requests.get(metrics_url, verify=CA_CERT, cert=(CLIENT_CERT, CLIENT_KEY), timeout=2)
        return resp.status_code == 200
    except:
        return False

def update_servers_status():
    for server in SERVERS:
        server["active"] = check_server_health(server)

@app.route('/data', methods=['POST'])
def proxy_to_server():
    update_servers_status()
    active_server = get_active_server()
    if not active_server:
        return jsonify({"status": "error", "message": "No active servers"}), 503
    
    try:
        client_data = request.get_data()
        resp = requests.post(active_server["url"], data=client_data, verify=CA_CERT, cert=(CLIENT_CERT, CLIENT_KEY), timeout=5)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        active_server["active"] = False
        return proxy_to_server()

@app.route('/metrics', methods=['GET'])
def get_all_metrics():
    update_servers_status()
    all_metrics = []
    for server in SERVERS:
        if server["active"]:
            try:
                metrics_url = f"https://localhost:{server['port']}/metrics"
                resp = requests.get(metrics_url, verify=CA_CERT, cert=(CLIENT_CERT, CLIENT_KEY), timeout=2)
                if resp.status_code == 200:
                    metrics = resp.json()
                    metrics["server_port"] = server["port"]
                    all_metrics.append(metrics)
            except:
                all_metrics.append({"server_port": server["port"], "active": False})
        else:
            all_metrics.append({"server_port": server["port"], "active": False})
    
    active_servers = [m for m in all_metrics if m.get("active") != False]
    if active_servers:
        total_rps = sum(m.get("rps", 0) for m in active_servers)
        avg_latency = sum(m.get("avg_latency_ms", 0) for m in active_servers) / len(active_servers)
    else:
        total_rps = 0
        avg_latency = 0
    
    return jsonify({
        "aggregated": {
            "total_rps": total_rps,
            "average_latency_ms": avg_latency,
            "active_servers_count": len(active_servers)
        },
        "servers": all_metrics
    })

@app.route('/health', methods=['GET'])
def health():
    update_servers_status()
    active_count = sum(1 for s in SERVERS if s["active"])
    return jsonify({"status": "ok", "active_servers": active_count, "total_servers": len(SERVERS)})

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(COORD_CERT, COORD_KEY)
    context.load_verify_locations(CA_CERT)
    context.verify_mode = ssl.CERT_REQUIRED
    
    app.run(host='0.0.0.0', port=8000, ssl_context=context, debug=False)
