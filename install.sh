#!/bin/bash
# ==============================================================================
#  TheNextEcho - Titan Edition - USER INSTALLER v1.2
# ==============================================================================
#  Ce script installe et configure la plateforme TheNextEcho sur votre système.
#  Il clone le code source, analyse le matériel, installe les dépendances
#  et configure l'environnement pour une exécution optimale.
# ==============================================================================

set -e
C_RESET='\033[0m'; C_RED='\033[0;31m'; C_GREEN='\033[0;32m'; C_YELLOW='\033[0;33m'; C_BLUE='\033[0;34m';
function print_info { echo -e "${C_BLUE}INFO: $1${C_RESET}"; }
function print_success { echo -e "${C_GREEN}SUCCÈS: $1${C_RESET}"; }
function print_warning { echo -e "${C_YELLOW}AVERTISSEMENT: $1${C_RESET}"; }
function print_header { echo -e "\n--- $1 ---"; }
function handle_error { echo -e "\n${C_RED}ERREUR: Échec de la commande '$1' à la ligne $2.${C_RESET}" >&2; exit 1; }
trap 'handle_error "$BASH_COMMAND" "$LINENO"' ERR
function check_command { command -v $1 &> /dev/null; }

# --- URL du dépôt contenant le code source complet ---
TEMPLATE_REPO_URL="https://github.com/smasmadigi/thenextecho-source.git" 
PROJECT_DIR="thenextecho"

# ========================
#  1. TÉLÉCHARGEMENT DU PROJET
# ========================
print_header "ÉTAPE 1: TÉLÉCHARGEMENT DU CODE SOURCE"
if [ -d "$HOME/$PROJECT_DIR" ]; then
    read -p "AVERTISSEMENT: Le dossier '$HOME/$PROJECT_DIR' existe. Le remplacer ? (oui/non): " REPLACE
    if [ "$REPLACE" = "oui" ]; then
        print_info "Suppression de l'installation existante..."
        rm -rf "$HOME/$PROJECT_DIR"
    else
        echo "Installation annulée."
        exit 0
    fi
fi
print_info "Clonage du projet depuis $TEMPLATE_REPO_URL..."
git clone "$TEMPLATE_REPO_URL" "$HOME/$PROJECT_DIR"
cd "$HOME/$PROJECT_DIR"

# ========================
#  2. ANALYSE ET CONFIGURATION DE L'ENVIRONNEMENT
# ========================
print_header "ÉTAPE 2: ANALYSE SYSTÈME ET CONFIGURATION"
RAM_GB=$(free -g|awk '/^Mem:/{print $2}'); CPU_CORES=$(nproc); HAS_GPU=false
if check_command nvidia-smi && nvidia-smi &> /dev/null; then HAS_GPU=true; fi
if [ "$RAM_GB" -lt 8 ]; then SUGGESTED_MODEL="qwen:0.5b"; elif [ "$RAM_GB" -lt 16 ]; then SUGGESTED_MODEL="phi3:mini"; else SUGGESTED_MODEL="llama3:8b"; fi
print_info "Système détecté: ${RAM_GB}GB RAM, ${CPU_CORES} coeurs CPU, GPU: ${HAS_GPU}."
print_info "Modèle IA par défaut suggéré : ${SUGGESTED_MODEL}."
ENV_FILE=".env"; rm -f "$ENV_FILE" backend/$ENV_FILE

print_info "Création du fichier de configuration .env..."
{
    echo "# Fichier de configuration pour TheNextEcho"
    echo "DATABASE_URL=sqlite:///./db/thenextecho.db"
    echo "SUGGESTED_MODEL=${SUGGESTED_MODEL}"
    echo "HAS_GPU=${HAS_GPU}"
    echo "CELERY_BROKER_URL=redis://localhost:6379/0"
    echo "CELERY_RESULT_BACKEND=redis://localhost:6379/0"
    echo "TTS_MODEL=tts_models/fr/mai/tacotron2-DDC"
    echo "VOCODER_MODEL=vocoder_models/fr/mai/hifigan_v1"
} >> "$ENV_FILE"
read -p "Entrez votre clé API Pexels: " PEXELS_API_KEY
echo "PEXELS_API_KEY=\"${PEXELS_API_KEY}\"" >> "$ENV_FILE"
# Copie ce .env dans le dossier backend pour qu'il soit accessible
mkdir -p backend
cp "$ENV_FILE" "backend/${ENV_FILE}"

# ========================
#  3. INSTALLATION DES DÉPENDANCES SYSTÈME
# ========================
print_header "ÉTAPE 3: INSTALLATION DES DÉPENDANCES SYSTÈME"
sudo -v || handle_error "Droits Sudo requis" "$LINENO"
print_info "Installation des paquets de base (git, curl, python, java, ffmpeg...)"
sudo apt-get update && sudo apt-get install -y git curl wget python3-pip python3-venv openjdk-21-jdk ffmpeg unzip imagemagick

if [ "${HAS_GPU}" = "true" ] && ! check_command nvidia-container-toolkit; then
    print_info "Installation du NVIDIA Container Toolkit pour le support GPU..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit; sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
fi

POLICY_FILE="/etc/ImageMagick-6/policy.xml"; if [ -f "$POLICY_FILE" ] && grep -q 'rights="none" pattern="@\*"' "$POLICY_FILE"; then sudo sed -i 's/<policy domain="path" rights="none" pattern="@\*" \/>/<!-- & -->/' "$POLICY_FILE"; fi

if ! getent group docker | grep -q "\b$USER\b"; then
    sudo usermod -aG docker $USER
    print_warning "ACTION REQUISE: L'utilisateur a été ajouté au groupe Docker. FERMEZ ce terminal, ouvrez-en un nouveau, puis relancez ce script."
    exit 1
fi

print_info "Installation de NVM et Node.js..."
export NVM_DIR="$HOME/.nvm"; if ! check_command nvm; then curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash; fi
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"; nvm install 20 && nvm use 20

# ========================
#  4. DÉPLOIEMENT DE L'INFRASTRUCTURE DOCKER
# ========================
print_header "ÉTAPE 4: DÉPLOIEMENT DES SERVICES DOCKER"
GPU_CONFIG=""; if [ "${HAS_GPU}" = "true" ]; then GPU_CONFIG=$(echo -e "deploy:\n      resources:\n        reservations:\n          devices: [{driver: nvidia, count: all, capabilities: [gpu]}]"); fi
OLLAMA_IMAGE="ollama/ollama"

cat <<EOF > docker-compose.yml
version: '3.8'
services:
  ollama:
    image: ${OLLAMA_IMAGE}
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - "thenextecho_ollama_data:/root/.ollama"
    restart: always
    ${GPU_CONFIG} # S'il est vide, rien ne sera ajouté. S'il a du contenu, il sera bien indenté.

  tts_server:
    image: ghcr.io/coqui-ai/tts-cpu
    container_name: tts_server
    ports:
      - "5002:5002"
    restart: always

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    restart: always

volumes:
  thenextecho_ollama_data:
    name: thenextecho_ollama_data # Nomme explicitement le volume
EOF

print_info "Lancement des conteneurs Ollama, TTS, et Redis..."
docker-compose up -d
print_info "Attente des services et téléchargement du modèle IA (${SUGGESTED_MODEL})..."
timeout=120; while ! curl -sf http://localhost:11434/api/tags > /dev/null; do ((timeout--)); if [ $timeout -le 0 ]; then handle_error "Ollama n'a pas démarré à temps." "$LINENO"; fi; sleep 1; done
docker-compose exec ollama ollama pull "${SUGGESTED_MODEL}"
print_success "Infrastructure prête."

# ========================
#  5. INSTALLATION DES DÉPENDANCES DU PROJET
# ========================
print_header "ÉTAPE 5: INSTALLATION DES DÉPENDANCES PYTHON & NODE.JS"
print_info "Installation des dépendances Python via pip et configuration du paquet local..."
(cd backend && { rm -rf venv; python3 -m venv venv; source venv/bin/activate; pip install --no-cache-dir -r requirements.txt; pip install -e .; alembic upgrade head; deactivate; })
print_info "Installation des dépendances Node.js via npm..."
(cd frontend && npm install)
print_success "Dépendances du projet installées."

# ========================
#  6. BUILD FINAL DU FRONTEND
# ========================
print_header "ÉTAPE 6: COMPILATION DU FRONTEND"
print_info "Compilation de l'application React pour la production..."
(cd frontend && npm run build)
print_success "Frontend compilé."

# ========================
#  CONCLUSION
# ========================
print_success "\nInstallation de TheNextEcho Titan Edition terminée !"
print_warning "Consultez le fichier README.md pour les instructions détaillées de lancement."
echo "Pour démarrer, vous devrez lancer les services dans plusieurs terminaux comme décrit dans la documentation."
