import logging
import sys

# 1. Setup the main server logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | [%(ip)s] | User: %(user)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("server_access.log"),
        logging.StreamHandler(sys.stdout) # Print to terminal screen too
    ]
)

# 2. Create a server connection helper class to inject metadata automatically
class ServerRequestContext(logging.LoggerAdapter):
    """Automatically adds IP and User identification to all log records"""
    def process(self, msg, kwargs):
        kwargs['extra'] = {
            'ip': self.extra.get('ip', '0.0.0.0'),
            'user': self.extra.get('user', 'ANONYMOUS')
        }
        return msg, kwargs

# 3. Simulate a server receiving connections
if __name__ == "__main__":
    print("Server log engine online. Writing to 'server_access.log'...")

    # Connection 1: Anonymous request
    conn1 = ServerRequestContext(logging.getLogger(), {'ip': '192.168.1.45'})
    conn1.info("GET /api/v1/status - HTTP 200 OK")

    # Connection 2: Authenticated user request
    conn2 = ServerRequestContext(logging.getLogger(), {'ip': '203.0.113.19', 'user': 'admin_alice'})
    conn2.warning("POST /api/v1/settings - HTTP 403 Forbidden (Insufficient permissions)")
    
    # Connection 3: System Exception handling
    try:
        raise ValueError("Database timeout on read query cluster-01")
    except Exception as e:
        conn2.exception("GET /api/v1/dashboard - HTTP 500 Internal Server Error")
