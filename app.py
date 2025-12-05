"""
SAML SSO Implementation for Render.com
Complete working code - just copy and paste!
"""

from flask import Flask, request, redirect, session, jsonify
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'render-saml-secret-key-change-in-production')

# Base URL - automatically uses Render's URL
BASE_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')

# SAML Settings
def get_saml_settings():
    return {
        "strict": False,
        "debug": True,
        "sp": {
            "entityId": f"{BASE_URL}/metadata/",
            "assertionConsumerService": {
                "url": f"{BASE_URL}/acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"{BASE_URL}/sls",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        },
        "idp": {
            "entityId": "https://samltest.id/saml/idp",
            "singleSignOnService": {
                "url": "https://samltest.id/idp/profile/SAML2/Redirect/SSO",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "singleLogoutService": {
                "url": "https://samltest.id/idp/profile/SAML2/Redirect/SLO",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": """MIIDEjCCAfqgAwIBAgIVAMECQ1tjghafm5OxWDh9hwZfxthWMA0GCSqGSIb3DQEB
CwUAMBYxFDASBgNVBAMMC3NhbWx0ZXN0LmlkMB4XDTE4MDgyNDIxMTQwOVoXDTM4
MDgyNDIxMTQwOVowFjEUMBIGA1UEAwwLc2FtbHRlc3QuaWQwggEiMA0GCSqGSIb3
DQEBAQUAA4IBDwAwggEKAoIBAQC0Z4QX1NFKs71ufbQwoQoW7qkNAJRIANGA4iM0
ThYghul3pC+FwrGv37aTxWXfA1UG9njKbbDreiDAZKngCgyjxj0uJ4lArgkr4AOE
jj5zXA81uGHARfUBctvQcsZpBIxDOvUUImAl+3NqLgMGF2fktxMG7kX3GEVNc1kl
bN3dfYsaw5dUrw25DheL9np7G/+28GwHPvLb4aptOiONbCaVvh9UMHEA9F7c0zfF
/cL5fOpdVa54wTI0u12CsFKt78h6lEGG5jUs/qX9clZncJM7EFkN3imPPy+0HC8n
spXiH/MZW8o2cqWRkrw3MzBZW3Ojk5nQj40V6NUbjb7kfejzAgMBAAGjVzBVMB0G
A1UdDgQWBBQT6Y9J3Tw/hOGc8PNV7JEE4k2ZNTA0BgNVHREELTArggtzYW1sdGVz
dC5pZIYcaHR0cHM6Ly9zYW1sdGVzdC5pZC9zYW1sL2lkcDANBgkqhkiG9w0BAQsF
AAOCAQEASk3guKfTkVhEaIVvxEPNR2w3vWt3fwmwJCccW98XXLWgNbu3YaMb2RSn
7Th4p3h+mfyk2don6au7Uyzc1Jd39RNv80TG5iQoxfCgphy1FYmmdaSfO8wvDtHT
TNiLArAxOYtzfYbzb5QrNNH/gQEN8RJaEf/g/1GTw9x/103dSMK0RXtl+fRs2nbl
D1JJKSQ3AdhxK/weP3aUPtLxVVJ9wMOQOfcy02l+hHMb6uAjsPOpOVKqi3M8XmcU
ZOpx4swtgGdeoSpeRyrtMvRwdcciNBp9UZome44qZAYH1iqrpmmjsfI9pJItsgWu
3kXPjhSfj1AJGR1l9JGvJrHki1iHTA=="""
        },
        "security": {
            "authnRequestsSigned": False,
            "wantAssertionsSigned": False,
            "wantMessagesSigned": False,
        }
    }

def prepare_request(request):
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }

# Routes
@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return f"""
        <html>
        <head>
            <title>SAML Login Success</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial; margin: 0; padding: 20px; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 700px; margin: 50px auto; background: white; padding: 40px; 
                             border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
                h1 {{ color: #667eea; margin-top: 0; font-size: 32px; }}
                .success {{ background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 25px; 
                           border-radius: 15px; border-left: 6px solid #28a745; margin: 25px 0; }}
                .info-box {{ background: #f8f9fa; padding: 18px; border-radius: 10px; margin: 12px 0; 
                            border-left: 4px solid #667eea; }}
                .btn {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; 
                       padding: 14px 30px; text-decoration: none; border-radius: 10px; display: inline-block; 
                       margin-top: 20px; font-weight: bold; box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4); 
                       transition: transform 0.2s; }}
                .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(220, 53, 69, 0.6); }}
                pre {{ background: #282c34; color: #61dafb; padding: 20px; border-radius: 10px; overflow: auto; 
                      font-size: 13px; line-height: 1.5; }}
                .badge {{ background: #667eea; color: white; padding: 6px 12px; border-radius: 20px; 
                         font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="badge">🚀 Powered by Render + SAML</div>
                <h1>✅ Successfully Authenticated!</h1>
                <div class="success">
                    <h2 style="margin-top:0; color: #155724;">Welcome, {user.get('name', 'User')}!</h2>
                    <p style="margin-bottom:0; color: #155724;">You have successfully logged in using SAML SSO.</p>
                </div>
                <div class="info-box"><strong>📧 Email:</strong> {user.get('email', 'N/A')}</div>
                <div class="info-box"><strong>👤 Username:</strong> {user.get('username', 'N/A')}</div>
                <div class="info-box"><strong>🔑 Name ID:</strong> {user.get('nameId', 'N/A')}</div>
                <h3 style="color: #333; margin-top: 30px;">📊 Full Session Data:</h3>
                <pre>{user}</pre>
                <a href="/logout" class="btn">🚪 Logout</a>
            </div>
        </body>
        </html>
        """
    else:
        return f"""
        <html>
        <head>
            <title>SAML SSO Demo - Render</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial; margin: 0; padding: 20px; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 750px; margin: 50px auto; background: white; padding: 45px; 
                             border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
                h1 {{ color: #667eea; margin-top: 0; font-size: 36px; }}
                .btn {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                       padding: 18px 40px; text-decoration: none; border-radius: 12px; display: inline-block; 
                       font-size: 20px; font-weight: bold; box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); 
                       transition: all 0.3s; }}
                .btn:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6); }}
                .info {{ background: linear-gradient(135deg, #e7f3ff 0%, #d6ebff 100%); padding: 25px; 
                        border-radius: 12px; border-left: 6px solid #667eea; margin: 25px 0; }}
                .steps {{ background: #f8f9fa; padding: 30px; border-radius: 12px; margin: 25px 0; }}
                .render-badge {{ background: linear-gradient(135deg, #46e3b7 0%, #00c896 100%); color: white; 
                                padding: 8px 18px; border-radius: 25px; font-size: 13px; font-weight: bold; 
                                display: inline-block; margin-bottom: 15px; }}
                ul {{ line-height: 2; }}
                li {{ margin: 12px 0; }}
                ol {{ line-height: 2; }}
                ol li {{ margin: 15px 0; }}
                a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="render-badge">🌐 Hosted on Render</div>
                <h1>🔐 SAML SSO Authentication</h1>
                <div class="info">
                    <strong>✨ Enterprise-Grade Authentication Demo</strong><br><br>
                    This application demonstrates SAML 2.0 Single Sign-On authentication.<br>
                    Using <strong>SAMLtest.id</strong> as the test Identity Provider.<br><br>
                    <strong>App URL:</strong> {BASE_URL}
                </div>
                
                <center><a href="/login" class="btn">🚀 Login with SAML SSO</a></center>
                
                <div class="steps">
                    <h3 style="color: #333; margin-top: 0;">📋 How it works:</h3>
                    <ol>
                        <li><strong>Click</strong> the "Login with SAML SSO" button above</li>
                        <li><strong>Redirect</strong> to SAMLtest.id (test Identity Provider)</li>
                        <li><strong>Enter</strong> any email format (e.g., test@example.com)</li>
                        <li><strong>Authenticate</strong> and get redirected back</li>
                        <li><strong>View</strong> your session data and attributes</li>
                    </ol>
                </div>
                
                <h3 style="color: #333;">🔗 API Endpoints:</h3>
                <ul>
                    <li><a href="/login"><strong>/login</strong></a> - Initiate SAML authentication</li>
                    <li><a href="/acs"><strong>/acs</strong></a> - Assertion Consumer Service (POST only)</li>
                    <li><a href="/metadata/"><strong>/metadata/</strong></a> - Service Provider Metadata (XML)</li>
                    <li><a href="/attrs"><strong>/attrs</strong></a> - View user attributes (JSON)</li>
                    <li><a href="/logout"><strong>/logout</strong></a> - Logout and end session</li>
                </ul>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107; margin-top: 30px;">
                    <strong>ℹ️ Note:</strong> This is a demonstration application. In production, you would integrate 
                    with your organization's Identity Provider (Okta, Azure AD, Google Workspace, etc.).
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/login')
def login():
    req = prepare_request(request)
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    return redirect(auth.login())

@app.route('/acs', methods=['POST'])
def acs():
    req = prepare_request(request)
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    auth.process_response()
    
    errors = auth.get_errors()
    if errors:
        error_reason = auth.get_last_error_reason()
        return f"""
        <html>
        <head>
            <title>Authentication Error</title>
            <style>
                body {{ font-family: Arial; margin: 50px; background: #f8d7da; }}
                .error {{ max-width: 600px; margin: auto; background: white; padding: 30px; 
                         border-radius: 10px; border-left: 5px solid #dc3545; }}
                h1 {{ color: #dc3545; }}
                pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow: auto; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>❌ Authentication Failed</h1>
                <p><strong>Reason:</strong> {error_reason}</p>
                <h3>Error Details:</h3>
                <pre>{errors}</pre>
                <a href="/" style="color: #007bff;">← Back to Home</a>
            </div>
        </body>
        </html>
        """, 400
    
    attrs = auth.get_attributes()
    session['user'] = {
        'name': attrs.get('cn', [''])[0] if attrs.get('cn') else 'User',
        'email': attrs.get('mail', [''])[0] if attrs.get('mail') else attrs.get('email', [''])[0] if attrs.get('email') else 'N/A',
        'username': attrs.get('uid', [''])[0] if attrs.get('uid') else 'N/A',
        'nameId': auth.get_nameid(),
        'sessionIndex': auth.get_session_index(),
        'all_attributes': attrs
    }
    
    return redirect('/')

@app.route('/logout')
def logout():
    req = prepare_request(request)
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    
    name_id = session.get('user', {}).get('nameId')
    session_index = session.get('user', {}).get('sessionIndex')
    
    session.clear()
    return redirect(auth.logout(name_id=name_id, session_index=session_index))

@app.route('/sls')
def sls():
    req = prepare_request(request)
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    url = auth.process_slo()
    errors = auth.get_errors()
    
    if errors:
        error_reason = auth.get_last_error_reason()
        return f"<h1>Logout Error</h1><p>{error_reason}</p><p>{errors}</p>", 400
    
    session.clear()
    if url:
        return redirect(url)
    return redirect('/')

@app.route('/metadata/')
def metadata():
    req = prepare_request(request)
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    
    if errors:
        return f"<h1>Metadata Error</h1><p>{errors}</p>", 500
    
    return metadata, 200, {'Content-Type': 'text/xml'}

@app.route('/attrs')
def attrs():
    if 'user' in session:
        return jsonify(session['user'])
    return jsonify({'error': 'Not logged in', 'message': 'Please login first at /login'}), 401

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'SAML SSO Demo'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*60}")
    print(f"  SAML SSO Application Starting...")
    print(f"  URL: {BASE_URL}")
    print(f"  Port: {port}")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=port)
