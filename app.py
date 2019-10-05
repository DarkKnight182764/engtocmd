from flask import Flask, escape, request, jsonify
from model_predict import predict
import re


def clean(ip):
    ip = ip.strip()
    # ip = ip.lower()
    ip = re.sub("\.", " .", ip)
    ip = re.sub(",", " ,", ip)
    ip = re.sub("\?", " ?", ip)
    ip = re.sub("!", " !", ip)
    ip = re.sub("'s", " is", ip)
    ip = ip.strip()
    return ip


def proc_slots(slots, ip):
    ret = {}
    ip = ip.split()
    slots = slots.split()
    assert len(slots) == len(ip)
    for i, slot in enumerate(slots):
        if not slot == "o":
            ret[slot] = ip[i]
    return ret


def check_num(s):
    try:
        float(s)
        return True
    except Exception as e:
        return False


app = Flask(__name__)


@app.route('/engtocmd', methods=["POST"])
def hello():
    oeng = str(request.json["eng"])
    eng = clean(oeng)
    prediction = predict(eng)
    print(prediction)
    intent = prediction["intent"]
    slots = proc_slots(prediction["slots"], eng)
    if "slots" in request.json:
        for k in request.json["slots"]:
            slots[k] = request.json["slots"][k]

    if intent == "mkdir":
        if "dirname" in slots:
            if "dirloc" in slots:
                return jsonify({
                    "cmd": ["cd " + slots["dirloc"], "mkdir " + slots["dirname"]]
                })
            else:
                return jsonify({
                    "cmd": ["mkdir " + slots["dirname"]]
                })
        if "dirname" not in slots:
            return jsonify({
                "res": "What do you want the directory to be named?",
                "slot": "dirname"
            })
    elif intent == "cd":
        if "dirname" not in slots:
            return jsonify({
                "res": "Which directory do  you want to move to?",
                "slot": "dirname"
            })
        else:
            return jsonify({
                "cmd": ["cd " + slots["dirname"]]
            })
    elif intent == "ls":
        if "dirname" not in slots:
            return jsonify({
                "cmd": ["ls"]
            })
        else:
            return jsonify({
                "cmd": ["cd " + slots["dirname"], "ls"]
            })
    elif intent == "touch":
        if "filname" not in slots:
            return jsonify({
                "res": "What should be the name of this new file?",
                "slot": "filname"
            })
        else:
            if "dirloc" not in slots:
                return jsonify({
                    "cmd": ["touch " + slots["filname"]]
                })
            else:
                return jsonify({
                    "cmd": ["cd " + slots["dirloc"], "touch " + slots["filname"]]
                })
    elif intent == "man":
        if "comname" not in slots:
            return jsonify({
                "res": "Which command do you want to know about?",
                "slot": "comname"
            })
        else:
            return jsonify({
                "cmd": ["man " + slots["comname"]]
            })
    # elif intent == "mv":
    #     if "mv_source" in slots and "mv_dest" in slots:
    #         return jsonify({
    #             "cmd": ["mv " + slots["mv_source"] + " " + slots["mv_dest"]]
    #         })
    #     elif "mv_source" not in slots:
    #         return jsonify({
    #             "res": "Which file do you wish to move?"
    #         })
    #     elif "mv_dest" not in slots:
    #         return jsonify({
    #             "res": "Where do you want this file to be moved?"
    #         })

    return "no intent detected"
