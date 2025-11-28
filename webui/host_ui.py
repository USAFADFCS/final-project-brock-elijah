from flask import Flask, request, jsonify, send_from_directory, make_response
import os
from pathlib import Path
from web_api.api_functions import Application_API


APP = Flask(__name__, static_folder=str(Path(__file__).parent / "site"))


def add_cors_headers(resp):
	resp.headers["Access-Control-Allow-Origin"] = "*"
	resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
	resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
	return resp


@APP.after_request
def _after_request(response):
	return add_cors_headers(response)


@APP.route("/", methods=["GET"])
def index():
	return send_from_directory(APP.static_folder, "index.html")


@APP.route("/<path:filename>", methods=["GET"])
def static_files(filename):
	return send_from_directory(APP.static_folder, filename)


# API endpoints
api = Application_API()


@APP.route("/api/get_all_tools", methods=["GET"])
def get_all_tools():
	tools = api.get_all_tools()
	return jsonify({"tools": tools})


@APP.route("/api/get_allowed_tools", methods=["GET"])
def get_allowed_tools():
	try:
		ai_level = int(request.args.get("aiLevel", 0))
	except Exception:
		ai_level = 0
	allowed = api.get_allowed_tools(ai_level)
	return jsonify({"allowed": allowed})


@APP.route("/api/run_analysis", methods=["POST"])
def run_analysis():
	data = request.get_json(force=True)
	if not data:
		return jsonify({"error": "missing JSON body"}), 400

	# Expecting {aiLevel, instructions, text, tools}
	try:
		out = api.run_analysis(data)
	except Exception as e:
		return jsonify({"error": f"server error: {e}"}), 500

	# Ensure JSON serializable
	return jsonify(out)


def run(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
	root = Path(__file__).parent
	print(f"Serving site from: {root / 'site'}")
	APP.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
	run()

