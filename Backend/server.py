from flask import Flask
from flask_cors import CORS

from routes import register_blueprints

app = Flask(__name__)
CORS(app)

register_blueprints(app)

if __name__ == "__main__":
    app.run(port=5001)



# REPORTS WILL BE HOW MANY WORDS REPEATED, EXAMPLES OF IT
# OR: Stutter Level / What Caused It (Full Word, Partial Word or Score) / Examples Found / Song and BPM Reccomendation / Maybe More
# Main Logic Before Sam Makes 3 Recordings Critical, Reports After

# More Specific Song Recs and Numbers Later
