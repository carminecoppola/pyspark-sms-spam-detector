#!/bin/bash

set -e

function error_exit {
    echo "[ERROR] $1" >&2
    exit 1
}

function show_loading {
    local pid=$1
    local delay=0.1
    local spinner=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    while kill -0 $pid 2>/dev/null; do
        for symbol in "${spinner[@]}"; do
            echo -ne "\r[INFO] Running NLP script... $symbol"
            sleep $delay
        done
    done
    echo -ne "\r[INFO] NLP script completed.           \n"
}

# --- STEP 1: Setup solo al primo lancio
if [ ! -f ".setup_done" ]; then
    # Decompressione
    if [ -f "iot-project-backup.zip" ]; then
        echo "[INFO] Decompressing project archive (ZIP)..."
        unzip -q iot-project-backup.zip -d iot-project-backup-tmp || error_exit "Failed to decompress ZIP archive."
    elif [ -f "iot-project-backup.tar.gz" ]; then
        echo "[INFO] Decompressing project archive (TAR.GZ)..."
        mkdir -p iot-project-backup-tmp
        tar -xzf iot-project-backup.tar.gz -C iot-project-backup-tmp || error_exit "Failed to decompress TAR.GZ archive."
    else
        error_exit "Project archive not found!"
    fi

    # Move dei contenuti
    if [ -d "iot-project-backup-tmp/iot-project-backup" ]; then
        mv iot-project-backup-tmp/iot-project-backup ./iot-project-backup || error_exit "Failed to move project directory."
    else
        mv iot-project-backup-tmp/* ./iot-project-backup || error_exit "Failed to move project files."
    fi

    rm -rf iot-project-backup-tmp

    # Env setup
    cd iot-project-backup || error_exit "Failed to enter project directory."
    echo "[INFO] Setting up virtual environment..."
    if [ ! -d "myenv" ]; then
        python3 -m venv myenv || error_exit "Failed to create virtual environment."
    fi
    source myenv/bin/activate || error_exit "Failed to activate virtual environment."
    echo "[INFO] Installing required Python packages..."
    pip install --upgrade pip
    pip install pyspark numpy pandas matplotlib scikit-learn nltk || error_exit "Failed to install Python packages."
    cd ..
    # Setup completo
    touch .setup_done
else
    echo "[INFO] Setup already done. Skipping to execution..."
fi

# --- STEP 2: Esecuzione
cd iot-project-backup || error_exit "Failed to enter project directory."
source myenv/bin/activate || error_exit "Failed to activate virtual environment."

dataset_dir="$(pwd)/src/ds"
export DATASET_PATH="$dataset_dir/SMSSpamCollection"
if [ ! -d "$dataset_dir" ]; then
    error_exit "Dataset directory not found: $dataset_dir"
fi

if [ ! -d "src" ]; then
    error_exit "Source directory (src) not found!"
fi
cd src

if [ ! -f "my_sms_spam.py" ]; then
    error_exit "NLP script (my_sms_spam.py) not found!"
fi

# --- STEP 3: Scelta modalità esecuzione
echo ""
echo "Come vuoi eseguire lo script?"
echo "  1) python3 (classico)"
echo "  2) spark-submit"
read -p "Scelta (1/2): " mode

case $mode in
    1)
        echo "[INFO] Running NLP script with python3..."
        python3 my_sms_spam.py > output.txt 2>&1 &
        ;;
    2)
        echo "[INFO] Running NLP script with spark-submit..."
        spark-submit my_sms_spam.py > output.txt 2>&1 &
        ;;
    *)
        error_exit "Scelta non valida."
        ;;
esac

script_pid=$!
show_loading $script_pid

echo "[INFO] Displaying output.txt..."
cat output.txt

