from flask import Flask, Response

app = Flask(__name__)

@app.route("/metadata")
def metadata():
    xml_str = """<EntityDescriptor entityID="https://rare-nourishment.up.railway.app/metadata">
    <SPSSODescriptor>
        <NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</NameIDFormat>
    </SPSSODescriptor>
</EntityDescriptor>"""
    return Response(xml_str, content_type="text/xml")

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
