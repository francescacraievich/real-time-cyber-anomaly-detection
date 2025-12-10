"""
Background worker that continuously calls Flask API to make predictions.
This populates the Prometheus metrics exposed by Flask.
Automatically stops when Flask API is no longer available.
"""

import time

import requests

API_BASE_URL = "http://localhost:5000"

# Counter for consecutive failures - stop if too many
MAX_CONSECUTIVE_FAILURES = 5


def check_flask_alive():
    """Check if Flask API is still running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def run_prediction_loop():
    """
    Continuously calls the Flask API to stream logs and make predictions.
    Also periodically evaluates the model to update F1/precision/recall metrics.
    Stops automatically when Flask API is no longer available.
    """
    # Wait for Flask to be ready
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    else:
        return

    iteration = 0
    consecutive_failures = 0

    # Run initial evaluation
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/evaluate", params={"sample_size": 1000}, timeout=60
        )
    except Exception:
        pass

    while True:
        try:
            iteration += 1

            # Check if Flask is still alive every 10 iterations
            if iteration % 10 == 0:
                if not check_flask_alive():
                    consecutive_failures += 1
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        break
                else:
                    consecutive_failures = 0

            # Call the stream endpoint to trigger predictions
            response = requests.get(
                f"{API_BASE_URL}/api/logs/stream",
                params={"window_size": 50},
                timeout=30,
            )

            if response.status_code == 200:
                consecutive_failures = 0  # Reset on success

            # Run evaluation every 10 iterations to update F1/precision/recall
            if iteration % 10 == 0:
                try:
                    requests.post(
                        f"{API_BASE_URL}/api/evaluate",
                        params={"sample_size": 500},
                        timeout=60,
                    )
                except Exception:
                    pass

            # Sleep between iterations
            time.sleep(2)

        except KeyboardInterrupt:
            print("[Prediction Worker] Stopped")
            break
        except requests.exceptions.ConnectionError:
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print("[Prediction Worker] Stopped")
                break
            time.sleep(5)
        except requests.exceptions.RequestException:
            time.sleep(5)
        except Exception:
            time.sleep(5)


if __name__ == "__main__":
    run_prediction_loop()
