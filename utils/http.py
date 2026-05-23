"""
Zero-dependency HTTP client using only Python standard library
"""

import socket
import ssl
import json
import gzip
from urllib.parse import urlparse, urlencode, parse_qs
from typing import Dict, Optional, Any, Union


class HTTPResponse:
    """HTTP Response wrapper"""
    
    def __init__(self, status: int, headers: Dict[str, str], body: bytes):
        self.status = status
        self.headers = headers
        self._body = body
        self._text = None
        self._json = None
    
    @property
    def text(self) -> str:
        """Get response body as text"""
        if self._text is None:
            encoding = self._get_encoding()
            self._text = self._body.decode(encoding, errors='replace')
        return self._text
    
    def json(self) -> Any:
        """Parse response body as JSON"""
        if self._json is None:
            self._json = json.loads(self.text)
        return self._json
    
    def _get_encoding(self) -> str:
        """Detect encoding from headers"""
        content_type = self.headers.get('content-type', '').lower()
        if 'charset=' in content_type:
            return content_type.split('charset=')[1].split(';')[0].strip()
        return 'utf-8'
    
    @property
    def ok(self) -> bool:
        """Check if response status is OK (200-299)"""
        return 200 <= self.status < 300


class HTTPClient:
    """Zero-dependency HTTP client"""
    
    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.default_headers = {
            'User-Agent': 'InfoSentry-CLI/1.0.0 (OSINT Research Tool)',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'close'
        }
    
    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None
    ) -> HTTPResponse:
        """Make HTTP request"""
        # Parse URL
        parsed = urlparse(url)
        
        # Add query parameters
        if params:
            query = parse_qs(parsed.query)
            query.update({k: [v] for k, v in params.items()})
            query_string = urlencode(query, doseq=True)
            url = parsed._replace(query=query_string).geturl()
            parsed = urlparse(url)
        
        # Prepare headers
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Prepare body
        body = None
        if json_data is not None:
            body = json.dumps(json_data).encode('utf-8')
            request_headers['Content-Type'] = 'application/json'
        elif data is not None:
            if isinstance(data, dict):
                body = urlencode(data).encode('utf-8')
                request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            else:
                body = data.encode('utf-8')
        
        # Determine port and SSL
        is_https = parsed.scheme == 'https'
        port = parsed.port or (443 if is_https else 80)
        host = parsed.hostname
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Wrap with SSL if HTTPS
            if is_https:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            
            # Connect
            sock.connect((host, port))
            
            # Build request
            request_lines = [f"{method.upper()} {path} HTTP/1.1"]
            request_headers['Host'] = host
            
            for key, value in request_headers.items():
                request_lines.append(f"{key}: {value}")
            
            if body:
                request_lines.append(f"Content-Length: {len(body)}")
            
            request_lines.append("")
            request_text = "\r\n".join(request_lines)
            
            # Send request
            sock.sendall(request_text.encode('utf-8'))
            if body:
                sock.sendall(body)
            
            # Receive response
            response_data = b""
            while True:
                try:
                    chunk = sock.recv(8192)
                    if not chunk:
                        break
                    response_data += chunk
                except socket.timeout:
                    break
            
            # Parse response
            return self._parse_response(response_data)
            
        finally:
            sock.close()
    
    def _parse_response(self, data: bytes) -> HTTPResponse:
        """Parse HTTP response"""
        # Find header/body separator
        header_end = data.find(b'\r\n\r\n')
        if header_end == -1:
            header_end = data.find(b'\n\n')
            header_data = data[:header_end].decode('utf-8', errors='replace')
            body = data[header_end + 2:]
        else:
            header_data = data[:header_end].decode('utf-8', errors='replace')
            body = data[header_end + 4:]
        
        # Parse status line and headers
        lines = header_data.split('\r\n')
        if len(lines) < 1:
            lines = header_data.split('\n')
        
        status_line = lines[0]
        status_parts = status_line.split()
        status = int(status_parts[1]) if len(status_parts) >= 2 else 0
        
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        # Handle chunked encoding
        if headers.get('transfer-encoding') == 'chunked':
            body = self._decode_chunked(body)
        
        # Handle gzip compression
        if headers.get('content-encoding') == 'gzip':
            try:
                body = gzip.decompress(body)
            except Exception:
                pass
        
        return HTTPResponse(status, headers, body)
    
    def _decode_chunked(self, data: bytes) -> bytes:
        """Decode chunked transfer encoding"""
        result = b""
        pos = 0
        while pos < len(data):
            # Find chunk size
            end = data.find(b'\r\n', pos)
            if end == -1:
                break
            chunk_size = int(data[pos:end].split(b';')[0], 16)
            if chunk_size == 0:
                break
            pos = end + 2
            result += data[pos:pos + chunk_size]
            pos += chunk_size + 2
        return result
    
    def get(self, url: str, **kwargs) -> HTTPResponse:
        """Make GET request"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> HTTPResponse:
        """Make POST request"""
        return self.request('POST', url, **kwargs)


# Global client instance
_client = HTTPClient()


def get(url: str, **kwargs) -> HTTPResponse:
    """Convenience function for GET requests"""
    return _client.get(url, **kwargs)


def post(url: str, **kwargs) -> HTTPResponse:
    """Convenience function for POST requests"""
    return _client.post(url, **kwargs)
