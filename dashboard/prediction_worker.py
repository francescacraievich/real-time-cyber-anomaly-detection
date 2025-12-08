"""
Background worker that continuously calls Flask API to make predictions.
This populates the Prometheus metrics exposed by Flask.
Automatically stops when Flask API is no longer available.
"""

import sys
import time
import requests
from pathlib import Path

API_BASE_URL = "http://localhost:5000"

# Counter for consecutive failures - stop if too many
MAX_CONSECUTIVE_FAILURES = 5


def check_flask_alive():
    """Check if Flask API is still running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def run_prediction_loop():
    """
    Continuously calls the Flask API to stream logs and make predictions.
    Also periodically evaluates the model to update F1/precision/recall metrics.
    Stops automatically when Flask API is no longer available.
    """
    print("[Prediction Worker] Starting...")
    print("[Prediction Worker] Will call Flask API to trigger predictions...")

    # Wait for Flask to be ready
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print("[Prediction Worker] Flask API is ready!")
                break
        except requests.exceptions.ConnectionError:
            print(f"[Prediction Worker] Waiting for Flask API... ({i+1}/10)")
            time.sleep(2)
    else:
        print("[Prediction Worker] ERROR: Flask API not available!")
        return

    iteration = 0
    consecutive_failures = 0

    # Run initial evaluation
    print("[Prediction Worker] Running initial model evaluation...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/evaluate", params={"sample_size": 1000}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"[Prediction Worker] Initial evaluation: F1={data['f1_score']:.3f} Precision={data['precision']:.3f} Recall={data['recall']:.3f}")
        else:
            print(f"[Prediction Worker] Initial evaluation failed: {response.status_code}")
    except Exception as e:
        print(f"[Prediction Worker] Initial evaluation error: {e}")

    print("[Prediction Worker] Starting continuous prediction loop...")

    while True:
        try:
            iteration += 1

            # Check if Flask is still alive every 10 iterations
            if iteration % 10 == 0:
                if not check_flask_alive():
                    consecutive_failures += 1
                    print(f"[Prediction Worker] Flask API not responding ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print("[Prediction Worker] Flask API down. Shutting down worker...")
                        break
                else:
                    consecutive_failures = 0

            # Call the stream endpoint to trigger predictions
            response = requests.get(
                f"{API_BASE_URL}/api/logs/stream",
                params={"window_size": 50},
                timeout=30
            )

            if response.status_code == 200:
                consecutive_failures = 0  # Reset on success
                data = response.json()
                logs = data.get("logs", [])

                # Count severities
                red_count = sum(1 for log in logs if log.get("severity") == "RED")
                orange_count = sum(1 for log in logs if log.get("severity") == "ORANGE")
                green_count = sum(1 for log in logs if log.get("severity") == "GREEN")

                if iteration % 5 == 0:
                    print(f"[Prediction Worker] Iteration {iteration}: {len(logs)} predictions - RED:{red_count} ORANGE:{orange_count} GREEN:{green_count}")

            else:
                print(f"[Prediction Worker] API error: {response.status_code}")

            # Run evaluation every 10 iterations to update F1/precision/recall
            if iteration % 10 == 0:
                try:
                    eval_response = requests.post(
                        f"{API_BASE_URL}/api/evaluate",
                        params={"sample_size": 500},
                        timeout=60
                    )
                    if eval_response.status_code == 200:
                        eval_data = eval_response.json()
                        print(f"[Prediction Worker] Evaluation: F1={eval_data['f1_score']:.3f} Precision={eval_data['precision']:.3f} Recall={eval_data['recall']:.3f} DetRate={eval_data['detection_rate']:.3f} FAR={eval_data['false_alarm_rate']:.3f}")
                except Exception as e:
                    print(f"[Prediction Worker] Evaluation error: {e}")

            # Sleep between iterations
            time.sleep(2)

        except KeyboardInterrupt:
            print("\n[Prediction Worker] Shutting down...")
            break
        except requests.exceptions.ConnectionError:
            consecutive_failures += 1
            print(f"[Prediction Worker] Connection error ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print("[Prediction Worker] Too many failures. Shutting down...")
                break
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"[Prediction Worker] Request error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"[Prediction Worker] Error in iteration {iteration}: {e}")
            time.sleep(5)

    print("[Prediction Worker] Stopped.")


if __name__ == "__main__":
    run_prediction_loop()
