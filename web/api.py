#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SENTRAX API - Version Complete avec sécurité avancée
JWT + 2FA + Rate limiting + Reset Password + Register
"""

from flask import (
    Flask,
    jsonify,
    request,
    render_template_string,
    send_file,
    redirect,
    Response
)

from flask_cors import CORS
from datetime import datetime, timedelta

import socket
import threading
import uuid
import io
import os
import sys
import sqlite3
import time
import base64
import secrets
import ipaddress
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from collections import defaultdict
from functools import wraps

from dotenv import load_dotenv

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import jwt
import pyotp
import qrcode

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# =========================================================
# CHARGEMENT ENV
# =========================================================

load_dotenv()

# =========================================================
# CHEMINS
# =========================================================

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# =========================================================
# FLASK
# =========================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

CORS(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    secrets.token_hex(64)
)

JWT_EXPIRATION_HOURS = int(
    os.getenv("JWT_EXPIRATION_HOURS", "8")
)

API_VERSION = "3.1.0"

# =========================================================
# CONFIGURATION EMAIL
# =========================================================

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@sentrax.com")

EMAIL_CONFIGURED = all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD])


def send_reset_email(email_to, username, reset_link):
    """Envoie un email de réinitialisation"""
    if not EMAIL_CONFIGURED:
        print(f"[EMAIL NON CONFIGURE] Lien de réinitialisation pour {username}: {reset_link}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM
        msg['To'] = email_to
        msg['Subject'] = "SENTRAX - Reinitialisation de votre mot de passe"

        body = f"""
        Bonjour {username},

        Vous avez demande la reinitialisation de votre mot de passe SENTRAX.

        Cliquez sur le lien ci-dessous (valable 1 heure) :
        {reset_link}

        Si vous n'etes pas a l'origine de cette demande, ignorez cet email.

        ---
        SENTRAX - Suite de cybersecurite professionnelle
        Site officiel : https://ndaye12.github.io/SentraX/
        Documentation : https://ndaye12.github.io/SentraX/docs.html

        © 2026 Patrick Ndaye - SENTRAX
        """

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] Envoye a {email_to}")
        return True

    except Exception as e:
        print(f"[EMAIL] Erreur: {e}")
        return False


# =========================================================
# VALIDATION MOT DE PASSE
# =========================================================

def validate_password_strength(password):
    """Vérifie la complexité du mot de passe"""
    if len(password) < 8:
        return False, "Au moins 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Au moins une majuscule"
    if not re.search(r'[a-z]', password):
        return False, "Au moins une minuscule"
    if not re.search(r'[0-9]', password):
        return False, "Au moins un chiffre"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Au moins un caractere special (!@#$%^&*...)"
    return True, "OK"


# =========================================================
# DATABASE
# =========================================================

DB_PATH = os.path.join(BASE_DIR, "sentrax.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            twofa_secret TEXT,
            twofa_enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            username TEXT,
            ip TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")

    if cursor.fetchone()[0] == 0:
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!")
        valid, _ = validate_password_strength(ADMIN_PASSWORD)
        if not valid:
            ADMIN_PASSWORD = "Admin123!"
        admin_pwd = generate_password_hash(ADMIN_PASSWORD)
        print(f"[SENTRAX] Compte admin: {ADMIN_PASSWORD}")

        cursor.execute("""
            INSERT INTO users (
                username, password, email, twofa_enabled
            ) VALUES (?, ?, ?, ?)
        """, ("admin", admin_pwd, "admin@sentrax.local", 0))

    conn.commit()
    conn.close()


init_db()

# =========================================================
# HELPERS DATABASE
# =========================================================


def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def update_user_email(username, email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))
    conn.commit()
    conn.close()


def create_user(username, password, email=None):
    hashed = generate_password_hash(password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, email) VALUES (?, ?, ?)
        """, (username, hashed, email))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success


def update_password(username, new_password):
    hashed = generate_password_hash(new_password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
    conn.commit()
    conn.close()


def save_reset_token(token, username, expires_at):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reset_tokens (token, username, expires_at) VALUES (?, ?, ?)
    """, (token, username, expires_at))
    conn.commit()
    conn.close()


def get_reset_token(token):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reset_tokens
        WHERE token = ? AND used = 0
        AND expires_at > strftime('%Y-%m-%d %H:%M:%S', 'now')
    """, (token,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def mark_token_used(token):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE reset_tokens SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def log_security_event(event_type, username, ip, details):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO security_logs (event_type, username, ip, details) VALUES (?, ?, ?, ?)
    """, (event_type, username, ip, details))
    conn.commit()
    conn.close()


def enable_2fa(username, secret):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET twofa_secret = ?, twofa_enabled = 1 WHERE username = ?
    """, (secret, username))
    conn.commit()
    conn.close()


def disable_2fa_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET twofa_enabled = 0, twofa_secret = NULL WHERE username = ?
    """, (username,))
    conn.commit()
    conn.close()


# =========================================================
# VALIDATION
# =========================================================

def validate_target(target):
    if not target:
        return False
    try:
        ipaddress.ip_address(target)
        return True
    except:
        pass
    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\.-]+\.[a-zA-Z]{2,}$'
    if re.match(domain_pattern, target):
        return True
    if target in ["localhost", "127.0.0.1", "scanme.nmap.org"]:
        return True
    return False


# =========================================================
# RATE LIMIT
# =========================================================

login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
BLOCK_DURATION = 300


def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        now = time.time()
        login_attempts[ip] = [t for t in login_attempts[ip] if now - t < BLOCK_DURATION]
        if len(login_attempts[ip]) >= MAX_ATTEMPTS:
            return jsonify({"error": "Trop de tentatives. Reessayez plus tard."}), 429
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            status_code = response[1]
        else:
            status_code = response.status_code
        if status_code == 401:
            login_attempts[ip].append(now)
        return response
    return decorated


# =========================================================
# JWT
# =========================================================

tokens_blacklist = set()


def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def verify_token(token):
    try:
        if token in tokens_blacklist:
            return None
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload
    except:
        return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token manquant"}), 401
        if token.startswith("Bearer "):
            token = token[7:]
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Token invalide ou expire"}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated


# =========================================================
# SCANNERS (10 scanners)
# =========================================================

SCANNERS = [
    {"id": "ai", "name": "AI Predictive Scanner", "desc": "Scan utilisant l'intelligence artificielle", "icon": "🤖"},
    {"id": "osint", "name": "OSINT Scanner", "desc": "Reconnaissance via Shodan, Censys, DNS", "icon": "🌐"},
    {"id": "p2p", "name": "P2P Scanner", "desc": "Scan distribue depuis plusieurs pays", "icon": "🤝"},
    {"id": "passive", "name": "Passive Scanner", "desc": "0 paquet envoye, indetectable", "icon": "👻"},
    {"id": "timemachine", "name": "Time Machine Scanner", "desc": "Analyse historique et predictions", "icon": "⏰"},
    {"id": "holo", "name": "Holographic Radar", "desc": "Visualisation 3D en temps reel", "icon": "🕶️"},
    {"id": "expert", "name": "Expert Scanner PRO", "desc": "SYN + UDP + OS detection", "icon": "👑"},
    {"id": "ultra", "name": "Ultra Scanner PRO", "desc": "UDP avance + ICMP + versions", "icon": "🔥"},
    {"id": "snmp", "name": "SNMP Scanner", "desc": "Detection de peripheriques SNMP", "icon": "🔌"},
    {"id": "dns", "name": "DNS Scanner", "desc": "Enumeration DNS et sous-domaines", "icon": "📡"}
]

scans = {}

# =========================================================
# HTML LOGIN (avec icône œil)
# =========================================================

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SENTRAX - Connexion</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0a0a0a;font-family:'Segoe UI',monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;}
.container{background:#1a1a1a;padding:40px;border-radius:10px;border:1px solid #00ff88;width:400px;}
.logo{text-align:center;font-size:48px;margin-bottom:20px;}
h1{color:#00ff88;text-align:center;margin-bottom:30px;}
input{width:100%;padding:12px;margin:10px 0;background:#0a0a0a;border:1px solid #00ff88;color:#00ff88;border-radius:5px;}
button{width:100%;padding:12px;background:#00ff88;color:#000;border:none;border-radius:5px;cursor:pointer;font-weight:bold;margin-top:10px;}
button:hover{background:#00cc66;}
.error{color:#ff4444;text-align:center;margin-top:10px;display:none;}
.success{color:#00ff88;text-align:center;margin-top:10px;display:none;}
.twofa-section{display:none;}
.links{margin-top:20px;text-align:center;border-top:1px solid #333;padding-top:20px;}
.links a{color:#00ff88;text-decoration:none;font-size:14px;margin:0 10px;cursor:pointer;}
.links a:hover{text-decoration:underline;color:#00cc66;}
.modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background-color:rgba(0,0,0,0.9);justify-content:center;align-items:center;}
.modal-content{background:#1a1a1a;border:2px solid #00ff88;border-radius:15px;padding:30px;width:400px;text-align:center;}
.modal-content input{width:100%;padding:12px;margin:10px 0;background:#0a0a0a;border:1px solid #00ff88;color:#00ff88;border-radius:5px;}
.modal-content button{background:#00ff88;color:#000;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;margin:5px;}
/* Ajout icône œil */
.password-container{position:relative;width:100%;}
.password-container input{width:100%;padding:12px;padding-right:40px;}
.password-toggle{position:absolute;right:10px;top:50%;transform:translateY(-50%);cursor:pointer;color:#00ff88;background:transparent;border:none;font-size:16px;}
</style>
</head>
<body>
<div class="container">
<div class="logo">🛡️</div>
<h1>SENTRAX</h1>
<div id="login-form">
    <input type="text" id="username" placeholder="Nom d'utilisateur">
    <div class="password-container">
        <input type="password" id="password" placeholder="Mot de passe">
        <span class="password-toggle" onclick="togglePassword('password')">👁️</span>
    </div>
    <div id="twofa-section" class="twofa-section">
        <input type="text" id="twofa" placeholder="Code 2FA">
    </div>
    <button id="login-btn">Se connecter</button>
    <div id="error" class="error"></div>
</div>
<div id="register-form" style="display:none;">
    <input type="text" id="reg-username" placeholder="Nom d'utilisateur">
    <input type="email" id="reg-email" placeholder="Email (optionnel)">
    <div class="password-container">
        <input type="password" id="reg-password" placeholder="Mot de passe (min 8, maj, min, chiffre, special)">
        <span class="password-toggle" onclick="togglePassword('reg-password')">👁️</span>
    </div>
    <div class="password-container">
        <input type="password" id="reg-confirm" placeholder="Confirmer le mot de passe">
        <span class="password-toggle" onclick="togglePassword('reg-confirm')">👁️</span>
    </div>
    <button id="register-btn">Creer mon compte</button>
    <div id="reg-error" class="error"></div>
    <div id="reg-success" class="success"></div>
</div>
<div class="links">
    <a href="#" id="show-register-link">📝 Creer un compte</a>
    <a href="#" id="show-login-link" style="display:none;">🔐 Deja un compte ? Se connecter</a>
    <a href="#" id="forgot-link">🔑 Mot de passe oublie ?</a>
</div>
</div>

<div id="modal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <h3 id="modalTitle" style="color:#00ff88;margin-bottom:20px;">Confirmation</h3>
        <div id="modalMessage" style="margin-bottom:15px;"></div>
        <div id="modalInputs"></div>
        <div id="modalButtons">
            <button type="button" id="modalOkBtn" onclick="confirmModal()">OK</button>
            <button type="button" id="modalCancelBtn" onclick="closeModal()">Annuler</button>
        </div>
    </div>
</div>

<script>
function togglePassword(id, btn){
    var x = document.getElementById(id);
    if(x.type === "password"){
        x.type = "text";
        btn.textContent = "🙈";
    }else{
        x.type = "password";
        btn.textContent = "👁️";
    }
}

var needTwofa = false;
var loginForm = document.getElementById('login-form');
var registerForm = document.getElementById('register-form');
var showRegisterLink = document.getElementById('show-register-link');
var showLoginLink = document.getElementById('show-login-link');
var forgotLink = document.getElementById('forgot-link');
var loginBtn = document.getElementById('login-btn');
var registerBtn = document.getElementById('register-btn');

var modal = document.getElementById('modal');
var modalCallback = null;

// === FONCTION POUR CONFIRMER LE MODAL (2 champs) ===
function confirmModal(){
    if(modalCallback){
        var input = document.getElementById('modalInput');
        var input1 = document.getElementById('modalInput1');
        var input2 = document.getElementById('modalInput2');
        if(input1 && input2){
            modalCallback(input1.value, input2.value);
        }else if(input){
            modalCallback(input.value);
        }else{
            modalCallback();
        }
    }
    closeModal();
}

function closeModal(){
    var modalElem = document.getElementById('modal');
    if(modalElem){
        modalElem.style.display = 'none';
    }
    modalCallback = null;
}
function showCustomModal(title, message, inputType, callback, keepOpen = false){
    var modalElem = document.getElementById('modal');
    if(!modalElem){
        console.error('Modal element not found');
        alert(message);
        return;
    }
    
    // Créer un callback spécial qui ne ferme pas automatiquement
    window.modalCallback = function(){
        var input = document.getElementById('modalInput');
        var input1 = document.getElementById('modalInput1');
        var input2 = document.getElementById('modalInput2');
        
        let result;
        if(input1 && input2){
            result = callback(input1.value, input2.value);
        }else if(input){
            result = callback(input.value);
        }else{
            result = callback();
        }
        
        // Ne fermer que si keepOpen est false OU si le callback retourne false
        if(!keepOpen || result === false) {
            closeModal();
        }
    };
    
    document.getElementById('modalTitle').innerHTML = title;
    document.getElementById('modalMessage').innerHTML = message;
    var inputsDiv = document.getElementById('modalInputs');
    inputsDiv.innerHTML = '';
    
    if(inputType === 'text'){
        inputsDiv.innerHTML = '<input type="text" id="modalInput" placeholder="Votre reponse" autocomplete="off">';
    }else if(inputType === 'password'){
        inputsDiv.innerHTML = '<input type="password" id="modalInput" placeholder="Votre reponse" autocomplete="off">';
    }else if(inputType === 'confirm'){
        inputsDiv.innerHTML = '<input type="password" id="modalInput1" placeholder="Nouveau mot de passe" autocomplete="off"><input type="password" id="modalInput2" placeholder="Confirmation" autocomplete="off">';
    }
    
    modalElem.style.display = 'flex';
    var input = document.getElementById('modalInput');
    if(input) input.focus();
}

// === ATTACHEMENT DES ÉVÉNEMENTS ===
var okBtn = document.getElementById('modalOkBtn');
var cancelBtn = document.getElementById('modalCancelBtn');

if(okBtn){
    okBtn.onclick = function(){ confirmModal(); };
}
if(cancelBtn){
    cancelBtn.onclick = function(){ closeModal(); };
}

window.onclick = function(event){
    var modalElem = document.getElementById('modal');
    if(event.target === modalElem){
        closeModal();
    }
};

if(showRegisterLink){
    showRegisterLink.onclick = function(e){
        e.preventDefault();
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        showRegisterLink.style.display = 'none';
        showLoginLink.style.display = 'inline';
    };
}
if(showLoginLink){
    showLoginLink.onclick = function(e){
        e.preventDefault();
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        showRegisterLink.style.display = 'inline';
        showLoginLink.style.display = 'none';
        var errorDiv = document.getElementById('error');
        if(errorDiv) errorDiv.style.display = 'none';
    };
}

async function doLogin(){
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var twofa = document.getElementById('twofa').value;
    var body = {username: username, password: password};
    if(needTwofa) body.twofa_code = twofa;
    try{
        var response = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        var data = await response.json();
        if(data.token){
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', username);
            window.location.href = '/dashboard';
        }else if(data.need_2fa){
            needTwofa = true;
            document.getElementById('twofa-section').style.display = 'block';
            showError('Code 2FA requis');
        }else{
            showError(data.error || 'Erreur de connexion');
        }
    }catch(err){
        showError('Erreur reseau');
    }
}

async function doRegister(){
    var username = document.getElementById('reg-username').value;
    var email = document.getElementById('reg-email').value;
    var password = document.getElementById('reg-password').value;
    var confirm = document.getElementById('reg-confirm').value;
    if(!username || !password){
        showRegError('Nom utilisateur et mot de passe requis');
        return;
    }
    if(password.length < 8){
        showRegError('Mot de passe trop court (min 8)');
        return;
    }
    if(password !== confirm){
        showRegError('Les mots de passe ne correspondent pas');
        return;
    }
    try{
        var response = await fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, email: email, password: password})
        });
        var data = await response.json();
        if(response.ok){
            var successDiv = document.getElementById('reg-success');
            successDiv.textContent = 'Compte cree ! Redirection...';
            successDiv.style.display = 'block';
            setTimeout(function(){
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
                showRegisterLink.style.display = 'inline';
                showLoginLink.style.display = 'none';
                document.getElementById('username').value = username;
                document.getElementById('password').value = '';
                successDiv.style.display = 'none';
            }, 2000);
        }else{
            showRegError(data.error);
        }
    }catch(err){
        showRegError('Erreur reseau');
    }
}

async function doForgot(){
    // Fonction pour réafficher le modal
    function askAgain() {
        showCustomModal('Reinitialisation', 'Entrez votre nom utilisateur SENTRAX', 'text', async function(username){
            if(!username) return;
            
            let response = await fetch('/api/forgot-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
            });
            
            let data = await response.json();
            
            if(data.link){
                // Message de succès
                showMessage('✅ Lien de réinitialisation envoyé !', 'success');
                setTimeout(function() {
                    closeModal();
                }, 2000);
            } else {
                // Message d'erreur (pas de fermeture)
                showMessage('❌ ' + (data.error || 'Utilisateur non trouvé'), 'error');
                askAgain(); // Rappelle pour réessayer
            }
        });
    }
    
    // Fonction pour afficher un message dans le modal
    function showMessage(msg, type) {
        var msgDiv = document.getElementById('modalMessage');
        msgDiv.innerHTML = msg;
        msgDiv.style.color = type === 'success' ? '#00ff88' : '#ff4444';
        setTimeout(function() {
            if(type !== 'error') {
                msgDiv.innerHTML = 'Entrez votre nom utilisateur SENTRAX';
                msgDiv.style.color = '';
            }
        }, 2000);
    }
    
    askAgain();
}
if(loginBtn) loginBtn.onclick = doLogin;
if(registerBtn) registerBtn.onclick = doRegister;
if(forgotLink) forgotLink.onclick = doForgot;

var passwordInput = document.getElementById('password');
if(passwordInput){
    passwordInput.onkeypress = function(e){
        if(e.key === 'Enter') doLogin();
    };
}

var regPasswordInput = document.getElementById('reg-password');
if(regPasswordInput){
    regPasswordInput.onkeypress = function(e){
        if(e.key === 'Enter') doRegister();
    };
}

function showError(msg){
    var errorDiv = document.getElementById('error');
    if(errorDiv){
        errorDiv.textContent = msg;
        errorDiv.style.display = 'block';
        setTimeout(function(){ errorDiv.style.display = 'none'; }, 3000);
    }
}

function showRegError(msg){
    var errorDiv = document.getElementById('reg-error');
    if(errorDiv){
        errorDiv.textContent = msg;
        errorDiv.style.display = 'block';
        setTimeout(function(){ errorDiv.style.display = 'none'; }, 3000);
    }
}
</script>
</body>
</html>
"""

# =========================================================
# HTML DASHBOARD
# =========================================================

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SENTRAX - Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body.dark{--bg:#0a0a0a;--card:#1a1a1a;--text:#00ff88;--border:#333;}
body.light{--bg:#f0f0f0;--card:#ffffff;--text:#000000;--border:#ddd;}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',monospace;transition:all 0.3s;}
.container{max-width:1400px;margin:0 auto;padding:20px;}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;padding:15px 20px;background:var(--card);border-radius:10px;flex-wrap:wrap;gap:10px;}
.logo h1{font-size:1.8em;color:#00ff88;}
.nav-buttons{display:flex;gap:10px;flex-wrap:wrap;}
.nav-btn{background:transparent;border:1px solid #00ff88;color:#00ff88;padding:8px 16px;border-radius:5px;cursor:pointer;}
.theme-btn{background:transparent;border:1px solid #ffaa00;color:#ffaa00;padding:8px 16px;border-radius:5px;cursor:pointer;}
.scan-section{background:var(--card);border-radius:10px;padding:20px;margin:20px 0;border:1px solid #00ff88;}
.scan-form{display:flex;gap:15px;flex-wrap:wrap;align-items:center;margin-top:15px;}
.scan-form input,.scan-form select{padding:12px;background:var(--bg);color:var(--text);border:1px solid #00ff88;border-radius:5px;}
.scan-form input{flex:2;min-width:200px;}
.btn-primary{background:#00ff88;color:#000;border:none;padding:12px 24px;border-radius:5px;cursor:pointer;font-weight:bold;}
.results{background:var(--card);border-radius:10px;padding:20px;margin:20px 0;display:none;border:1px solid #00ff88;}
.results.active{display:block;}
.button-group{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap;}
.btn-pdf{background:#00ff88;color:#000;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;}
.btn-email{background:#ff6600;color:#fff;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;}
.btn-security{background:#00aaff;color:#fff;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;}
pre{background:var(--bg);padding:15px;overflow-x:auto;border-radius:5px;max-height:400px;}
.history-table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;}
.history-table th,.history-table td{border:1px solid var(--border);padding:12px;text-align:left;}
.history-container{max-height:400px;overflow-y:auto;margin:20px 0;}
.status-completed{color:#00ff88;}
.status-running{color:#ffaa00;}
.status-failed{color:#ff4444;}
.loading{display:none;text-align:center;margin:30px;}
.loading.active{display:block;}
.spinner{border:3px solid #333;border-top:3px solid #00ff88;border-radius:50%;width:50px;height:50px;animation:spin 1s linear infinite;margin:0 auto 15px;}
@keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
.footer{text-align:center;margin-top:30px;padding:20px;border-top:1px solid var(--border);color:#666;font-size:12px;}
.scanner-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin:30px 0;}
.scanner-card{background:var(--card);border:1px solid #00ff88;border-radius:10px;padding:20px;cursor:pointer;transition:transform 0.3s;}
.scanner-card:hover{transform:translateY(-5px);}
.scanner-icon{font-size:2.5em;margin-bottom:10px;}
.scanner-name{font-size:1.2em;font-weight:bold;margin-bottom:5px;}
.scanner-desc{font-size:0.8em;color:#888;margin-bottom:15px;}
.scanner-btn{background:#00ff88;color:#000;border:none;padding:8px 16px;border-radius:5px;cursor:pointer;width:100%;}
.help-section{background:var(--card);border-radius:10px;padding:25px;margin:20px 0;}
.help-section h2{color:#00ff88;margin-bottom:15px;}
.help-section ul{margin-left:30px;}
.help-section li{margin:8px 0;}
.page{display:none;}
.page.active{display:block;}
.chart-container{width:100%;max-width:450px;margin:20px auto;}
.modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;background-color:rgba(0,0,0,0.9);justify-content:center;align-items:center;}
.modal-content{background:#1a1a1a;border:2px solid #00ff88;border-radius:15px;padding:30px;width:450px;max-width:90%;text-align:center;}
.modal-content input{width:100%;padding:12px;margin:10px 0;background:#0a0a0a;border:1px solid #00ff88;color:#00ff88;border-radius:5px;font-size:14px;}
.modal-content button{background:#00ff88;color:#000;border:none;padding:10px 25px;border-radius:5px;cursor:pointer;font-weight:bold;margin:5px;}
.modal-content button:hover{background:#00cc66;}
.modal-content .close{color:#ff4444;float:right;font-size:28px;font-weight:bold;cursor:pointer;}
.modal-content .close:hover{color:#ff8888;}
@media (max-width:768px){.container{padding:10px;}.nav-buttons{justify-content:center;}.history-table{font-size:12px;}}
.password-container{position:relative;width:100%;margin:10px 0;}
.password-container input{width:100%;padding:12px;padding-right:45px;box-sizing:border-box;}
.password-toggle{position:absolute;right:12px;top:50%;transform:translateY(-50%);cursor:pointer;}
</style>
</head>
<body>

<script id="scanners-data" type="application/json">
{{ scanners | tojson | safe }}
</script>

<div id="modal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <h3 id="modalTitle" style="color:#00ff88;margin-bottom:20px;">Confirmation</h3>
        <div id="modalMessage" style="margin-bottom:15px;"></div>
        <div id="modalInputs"></div>
        <div id="modalButtons">
            <button type="button" onclick="confirmModal()">Confirmer</button>
            <button type="button" onclick="closeModal()">Annuler</button>
        </div>
    </div>
</div>

<script>
var token=localStorage.getItem('token');
if(!token){
    window.location.href='/login';
}
var currentScanId=null;
var currentTheme=localStorage.getItem('theme')||'dark';
document.body.className=currentTheme;

var modalCallback=null;
var modalValue=null;
window.showModal = function(title, message, inputType, callback){
    var modalElem = document.getElementById('modal');
    if(!modalElem){
        alert(message);
        return;
    }
    
    window.modalCallback = callback;
    document.getElementById('modalTitle').innerHTML = title;
    document.getElementById('modalMessage').innerHTML = message;
    var inputsDiv = document.getElementById('modalInputs');
    inputsDiv.innerHTML = '';
    
    if(inputType === 'text'){
        inputsDiv.innerHTML = '<input type="text" id="modalInput" placeholder="Votre reponse" autocomplete="off" style="width:100%;padding:12px;margin:10px 0;background:var(--bg);color:var(--text);border:1px solid #00ff88;border-radius:5px;">';
    }else if(inputType === 'password'){
        inputsDiv.innerHTML = '<div class="password-container"><input type="password" id="modalInput" placeholder="Votre reponse" autocomplete="off"><span class="password-toggle" onclick="togglePassword(\'modalInput\', this)">👁️</span></div>';
    }else if(inputType === 'confirm'){
        inputsDiv.innerHTML = '<div class="password-container"><input type="password" id="modalInput1" placeholder="Nouveau mot de passe" autocomplete="off"><span class="password-toggle" onclick="togglePassword(\'modalInput1\', this)">👁️</span></div><div class="password-container"><input type="password" id="modalInput2" placeholder="Confirmation" autocomplete="off"><span class="password-toggle" onclick="togglePassword(\'modalInput2\', this)">👁️</span></div>';
        window.modalCallback = function(p1, p2){ callback(p1, p2); };
    }else{
        inputsDiv.innerHTML = '';
    }
    
    modalElem.style.display = 'flex';
    var firstInput = document.getElementById('modalInput');
    if(firstInput) firstInput.focus();
};

var isNestedModal = false;

window.confirmModal = function(){
    if(modalCallback){
        var input = document.getElementById('modalInput');
        var input1 = document.getElementById('modalInput1');
        var input2 = document.getElementById('modalInput2');
        
        var callback = modalCallback;
        
        if(input1 && input2){
            callback(input1.value, input2.value);
        }else if(input){
            callback(input.value);
        }else{
            callback();
        }
        
        // Fermer APRÈS que le nouveau modal se soit ouvert
        setTimeout(function() {
            var modalElem = document.getElementById('modal');
            // Vérifier si le modal n'a pas été réutilisé
            if(modalElem && modalElem.style.display === 'flex') {
                // Ne fermer que si c'est le même modal (pas un nouveau)
                // Pour l'instant, on le laisse ouvert
            }
        }, 100);
    }
};
window.closeModal = function(){
    var modalElem = document.getElementById('modal');
    if(modalElem){
        modalElem.style.display = 'none';
    }
    window.modalCallback = null;
};
window.showAlert = function(message){
    var modalElem = document.getElementById('modal');
    if(modalElem){
        document.getElementById('modalTitle').innerHTML = 'Information';
        document.getElementById('modalMessage').innerHTML = message;
        document.getElementById('modalInputs').innerHTML = '';
        modalElem.style.display = 'flex';
        modalCallback = function(){ modalElem.style.display = 'none'; };
    }else{
        alert(message);
    }
};
window.showConfirm = function(message, callback){
    document.getElementById('modalTitle').innerHTML = 'Confirmation';
    document.getElementById('modalMessage').innerHTML = message;
    document.getElementById('modalInputs').innerHTML = '';
    document.getElementById('modal').style.display = 'flex';
    modalCallback = function(){
        closeModal();
        if(callback) callback();
    };
};
window.showPage=function(pageName){
    var pages=document.querySelectorAll('.page');
    for(var i=0;i<pages.length;i++){
        pages[i].classList.remove('active');
    }
    var targetPage=document.getElementById(pageName+'-page');
    if(targetPage) targetPage.classList.add('active');
};

window.toggleTheme=function(){
    var newTheme=currentTheme==='dark'?'light':'dark';
    document.body.className=newTheme;
    localStorage.setItem('theme',newTheme);
    currentTheme=newTheme;
};

window.logout=function(){
    var currentToken=localStorage.getItem('token');
    if(currentToken){
        fetch('/api/logout',{
            method:'POST',
            headers:{'Authorization':'Bearer '+currentToken}
        }).catch(function(){});
    }
    localStorage.removeItem('token');
    window.location.href='/login';
};

window.showPage = function(pageName){
    var pages = document.querySelectorAll('.page');
    for(var i = 0; i < pages.length; i++){
        pages[i].classList.remove('active');
    }
    var targetPage = document.getElementById(pageName + '-page');
    if(targetPage) targetPage.classList.add('active');
};

window.toggleTheme = function(){
    var currentTheme = localStorage.getItem('theme') || 'dark';
    var newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.className = newTheme;
    localStorage.setItem('theme', newTheme);
};

window.startScan = function(){
    var target = document.getElementById('target').value.trim();
    var scanner = document.getElementById('scanner-select').value;
    if(!target){
        window.showAlert('Entrez une cible');
        return;
    }
    document.getElementById('loading').classList.add('active');
    document.getElementById('results').classList.remove('active');
    
    window.fetchWithAuth('/api/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({target: target, scanner: scanner})
    })
    .then(function(res){ return res.json(); })
    .then(function(data){
        if(data.scan_id){
            window.currentScanId = data.scan_id;
            window.saveToHistory(data.scan_id, target, scanner, 'running', null);
            window.checkScanStatus(data.scan_id);
        }
    })
    .catch(function(err){
        document.getElementById('loading').classList.remove('active');
        window.showAlert('Erreur: ' + err.message);
    });
};

window.startScan=function(){
    var targetInput=document.getElementById('target');
    var scannerSelect=document.getElementById('scanner-select');
    if(!targetInput||!scannerSelect) return;
    var target=targetInput.value.trim();
    var scanner=scannerSelect.value;
    if(!target){showAlert('Entrez une cible');return;}
    var loadingDiv=document.getElementById('loading');
    var resultsDiv=document.getElementById('results');
    if(loadingDiv) loadingDiv.classList.add('active');
    if(resultsDiv) resultsDiv.classList.remove('active');
    
    window.fetchWithAuth('/api/scan',{ 
        method:'POST', 
        headers:{'Content-Type':'application/json'}, 
        body:JSON.stringify({target:target,scanner:scanner}) 
    })
    .then(function(res){return res.json();})
    .then(function(data){ 
        if(data.scan_id){
            currentScanId=data.scan_id;
            saveToHistory(data.scan_id,target,scanner,'running',null);
            checkScanStatus(data.scan_id);
        }
    })
    .catch(function(err){ 
        var loadingDiv=document.getElementById('loading');
        if(loadingDiv) loadingDiv.classList.remove('active'); 
        showAlert('Erreur: '+err.message); 
    });
};

window.exportPDF=function(){ 
    if(currentScanId) window.open('/api/export/pdf/'+currentScanId,'_blank'); 
};

window.sendEmailReport=function(){ 
    if(currentScanId) showAlert('Fonction email - A configurer'); 
};

window.changePassword = function () {
    
    function askOldPassword() {
        window.showModal(
            'Verification',
            'Entrez votre ancien mot de passe',
            'password',
            function (oldPwd) {
                if (!oldPwd) {
                    askOldPassword(); // Re-demander si vide
                    return;
                }
                
                askNewPassword(oldPwd);
            }
        );
    }
    
    function askNewPassword(oldPwd) {
        window.showModal(
            'Changer mot de passe',
            'Entrez votre nouveau mot de passe',
            'confirm',
            function (newPwd, confirmPwd) {
                if (!newPwd || !confirmPwd) {
                    window.showAlert("Veuillez remplir les deux champs");
                    askNewPassword(oldPwd); // Re-demander
                    return;
                }
                
                if (newPwd !== confirmPwd) {
                    window.showAlert("Les mots de passe ne correspondent pas");
                    askNewPassword(oldPwd); // Re-demander
                    return;
                }
                
                // Envoyer à l'API
                fetch('/api/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('token')
                    },
                    body: JSON.stringify({
                        old_password: oldPwd,
                        new_password: newPwd
                    })
                })
                .then(function(response) {
                    return response.json().then(function(data) {
                        if (response.ok) {
                            window.showAlert("✅ " + (data.message || "Mot de passe changé avec succès"));
                            // Succès, on ne recommence pas
                        } else {
                            // Gestion des erreurs selon le code
                            if (data.code === "INVALID_OLD_PASSWORD") {
                                window.showAlert("❌ Ancien mot de passe incorrect");
                                askOldPassword(); // Recommencer depuis le début
                            } else if (data.code === "WEAK_PASSWORD") {
                                window.showAlert("❌ " + data.error);
                                askNewPassword(oldPwd); // Re-demander le nouveau
                            } else {
                                window.showAlert("❌ " + (data.error || "Erreur"));
                                askOldPassword(); // Recommencer
                            }
                        }
                    });
                })
                .catch(function(err) {
                    window.showAlert("❌ Erreur: " + err.message);
                    askOldPassword(); // Recommencer
                });
            }
        );
    }
    
    // Démarrer
    askOldPassword();
};
window.setup2FA = function(){
    window.fetchWithAuth('/api/2fa/setup', {method:'POST'})
    .then(function(res){ return res.json(); })
    .then(function(data){
        if(data.qr_code){
            var win = window.open('', '_blank', 'width=550,height=650');
            win.document.write(`
                <html><head><title>SENTRAX - 2FA Setup</title>
                <style>
                    body{background:#0a0a0a;color:#00ff88;font-family:monospace;text-align:center;padding:20px;}
                    .message{position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#00ff88;color:#000;padding:12px 20px;border-radius:5px;z-index:10000;display:none;}
                    input{padding:10px;margin:10px;background:#0a0a0a;border:1px solid #00ff88;color:#00ff88;border-radius:5px;}
                    button{background:#00ff88;padding:10px 20px;border:none;cursor:pointer;border-radius:5px;font-weight:bold;}
                </style>
                </head><body>
                <div id="customAlert" class="message"></div>
                <h1>🛡️ SENTRAX 2FA</h1>
                <p>Scannez ce QR code avec Google Authenticator</p>
                <img src="${data.qr_code}"><br>
                <p>Ou saisissez ce code : <strong>${data.secret}</strong></p>
                <input type="text" id="code" placeholder="Code 2FA" style="padding:10px;margin:10px;"><br>
                <button onclick="verify()">Vérifier</button>
                <script>
                    function showMessage(msg, isError){
                        var alertDiv = document.getElementById('customAlert');
                        alertDiv.textContent = msg;
                        alertDiv.style.backgroundColor = isError ? '#ff4444' : '#00ff88';
                        alertDiv.style.color = isError ? '#fff' : '#000';
                        alertDiv.style.display = 'block';
                        setTimeout(function(){
                            alertDiv.style.display = 'none';
                        }, 2000);
                    }
                    
                    async function verify(){
                        var code = document.getElementById('code').value;
                        if(!code){
                            showMessage('Veuillez entrer le code 2FA', true);
                            return;
                        }
                        try {
                            var response = await fetch('/api/2fa/verify', {
                                method:'POST',
                                headers:{
                                    'Authorization':'Bearer ${localStorage.getItem('token')}',
                                    'Content-Type':'application/json'
                                },
                                body:JSON.stringify({secret:'${data.secret}', code:code})
                            });
                            var result = await response.json();
                            if(response.ok){
                                showMessage(result.message || '✅ 2FA activée avec succès!', false);
                                setTimeout(function(){ window.close(); }, 1500);
                            } else {
                                showMessage(result.error || '❌ Code invalide', true);
                            }
                        } catch(err) {
                            showMessage('❌ Erreur: ' + err.message, true);
                        }
                    }
                <\/script>
                </body></html>
            `);
        }
    });
};

window.disable2FA=function(){
    showModal('Desactiver 2FA','Entrez votre code 2FA','text',function(code){
        window.fetchWithAuth('/api/2fa/disable',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({code:code})
        })
        .then(function(res){return res.json();})
        .then(function(data){
            showAlert(data.message||data.error);
        });
    });
};

window.togglePassword = function(id, btn){
    console.log("Toggle appelé pour:", id);  // Pour debug
    var x = document.getElementById(id);
    
    if (!x) {
        console.error("Element introuvable:", id);
        return;
    }
    
    if(x.type === "password"){
        x.type = "text";
        btn.textContent = "🙈";
    }else{
        x.type = "password";
        btn.textContent = "👁️";
    }
};
window.fetchWithAuth = function(url, options){

    if(!options) options = {};

    var token = localStorage.getItem('token');

    options.headers = options.headers || {};
    options.headers['Authorization'] = 'Bearer ' + token;

    return fetch(url, options).then(function(res){

        // 🔴 uniquement vrai problème session
        if(res.status === 401){
            window.showAlert("Session expirée");
            localStorage.removeItem('token');
            window.location.href = '/login';
            throw new Error("Unauthorized");
        }

        return res;
    });
};
window.fetchWithAuth=fetchWithAuth;

function checkScanStatus(scanId){
    fetchWithAuth('/api/scan/'+scanId).then(function(res){return res.json();}).then(function(data){
        if(data.status==='completed'){
            var loadingDiv=document.getElementById('loading');
            var resultsContent=document.getElementById('results-content');
            var resultsDiv=document.getElementById('results');
            if(loadingDiv) loadingDiv.classList.remove('active');
            if(resultsContent) resultsContent.textContent=JSON.stringify(data.results,null,2);
            if(resultsDiv) resultsDiv.classList.add('active');
            saveToHistory(scanId,data.target,data.scanner,'completed',data);
            if(data.results&&data.results.open_ports) updateChart(data.results);
        }else if(data.status==='failed'){
            var loadingDiv=document.getElementById('loading');
            if(loadingDiv) loadingDiv.classList.remove('active');
            showAlert('Scan echoue');
            saveToHistory(scanId,data.target,data.scanner,'failed',null);
        }else{
            setTimeout(function(){checkScanStatus(scanId);},2000);
        }
    });
}

function saveToHistory(scanId,target,scanner,status,results){
    var history=JSON.parse(localStorage.getItem('scan_history')||'[]');
    history.push({id:scanId,target:target,scanner:scanner,status:status,date:new Date().toISOString(),results:results});
    if(history.length>100) history.shift();
    localStorage.setItem('scan_history',JSON.stringify(history));
    loadHistory();
}

function loadHistory(){
    var history=JSON.parse(localStorage.getItem('scan_history')||'[]');
    var tbody=document.getElementById('history-body');
    if(!tbody) return;
    tbody.innerHTML='';
    for(var i=history.length-1;i>=0&&i>=history.length-20;i--){
        var scan=history[i];
        var row=tbody.insertRow();
        row.insertCell(0).textContent=scan.id;
        row.insertCell(1).textContent=scan.target;
        row.insertCell(2).textContent=scan.scanner||'expert';
        row.insertCell(3).innerHTML='<span class="status-'+scan.status+'">'+scan.status+'</span>';
        row.insertCell(4).textContent=new Date(scan.date).toLocaleString();
    }
}

function loadScanners(){
    var dataElement=document.getElementById('scanners-data');
    if(!dataElement) return;
    var scanners=JSON.parse(dataElement.textContent);
    var grid=document.getElementById('scanner-grid');
    if(!grid) return;
    grid.innerHTML='';
    for(var i=0;i<scanners.length;i++){
        var s=scanners[i];
        var card=document.createElement('div');
        card.className='scanner-card';
        card.innerHTML='<div class="scanner-icon">'+s.icon+'</div>'+
                       '<div class="scanner-name">'+s.name+'</div>'+
                       '<div class="scanner-desc">'+s.desc+'</div>'+
                       '<button class="scanner-btn" data-id="'+s.id+'">Utiliser</button>';
        
        var btn=card.querySelector('.scanner-btn');
        btn.addEventListener('click',(function(scannerId){
            return function(event){
                event.stopPropagation();
                var select=document.getElementById('scanner-select');
                if(select) select.value=scannerId;
                window.showPage('dashboard');
            };
        })(s.id));
        
        card.addEventListener('click',(function(scannerId){
            return function(){
                var select=document.getElementById('scanner-select');
                if(select) select.value=scannerId;
                window.showPage('dashboard');
            };
        })(s.id));
        
        grid.appendChild(card);
    }
}

function updateChart(results){
    if(typeof Chart==='undefined'){
        console.warn('Chart.js non charge');
        return;
    }
    var ctx=document.getElementById('statsChart').getContext('2d');
    var openPorts=results.open_ports||[];
    if(window.myChart) window.myChart.destroy();
    window.myChart=new Chart(ctx,{ 
        type:'bar', 
        data:{ 
            labels:openPorts.map(function(p){return 'Port '+p.port;}), 
            datasets:[{label:'Ports ouverts',data:openPorts.map(function(){return 1;}),backgroundColor:'#00ff88'}] 
        }, 
        options:{responsive:true} 
    });
}

document.addEventListener('DOMContentLoaded', function() {
    loadScanners();
    loadHistory();
});
setInterval(function(){
    var t=localStorage.getItem('token');
    if(t){
        fetch('/api/verify',{headers:{'Authorization':'Bearer '+t}}).catch(function(){});
    }
},60000);
</script>

<div class="container">
<div class="header">
    <div class="logo"><h1>SENTRAX</h1><p>Cybersecurity Scanner</p></div>
    <div class="nav-buttons">
        <button class="nav-btn" onclick="window.showPage('dashboard')">Dashboard</button>
        <button class="nav-btn" onclick="window.showPage('scanners')">Scanners</button>
        <button class="nav-btn" onclick="window.showPage('security')">Securite</button>
        <button class="nav-btn" onclick="window.showPage('help')">Aide</button>
        <button class="theme-btn" onclick="window.toggleTheme()">Theme</button>
        <button class="nav-btn" onclick="window.logout()">Logout</button>
    </div>
</div>

<div id="dashboard-page" class="page active">
    <div class="scan-section">
        <h2>Nouveau scan</h2>
        <div class="scan-form">
            <input type="text" id="target" placeholder="IP ou domaine" value="scanme.nmap.org">
            <select id="scanner-select">
                {% for s in scanners %}
                <option value="{{ s.id }}">{{ s.icon }} {{ s.name }}</option>
                {% endfor %}
            </select>
            <button class="btn-primary" onclick="window.startScan()">Lancer le scan</button>
        </div>
    </div>
    <div class="loading" id="loading"><div class="spinner"></div><p>Scan en cours...</p></div>
    <div class="results" id="results"><h3>Resultats du scan</h3><pre id="results-content"></pre><div class="button-group"><button class="btn-pdf" onclick="window.exportPDF()">Exporter PDF</button><button class="btn-email" onclick="window.sendEmailReport()">Envoyer par email</button></div></div>
    <div class="chart-container"><canvas id="statsChart"></canvas></div>
    <h3>Historique des scans</h3>
    <div class="history-container">
        <table class="history-table" id="history-table">
            <thead><tr><th>ID</th><th>Cible</th><th>Scanner</th><th>Statut</th><th>Date</th></tr></thead>
            <tbody id="history-body"><tr><td colspan="5">Chargement...</td></tr></tbody>
        </table>
    </div>
</div>

<div id="scanners-page" class="page"><h2>Scanners disponibles</h2><div id="scanner-grid" class="scanner-grid"></div></div>

<div id="security-page" class="page">
    <div class="scan-section">
        <h2>🔐 Securite du compte</h2>
        <div class="button-group">
            <button class="btn-security" onclick="window.changePassword()">🔑 Changer mot de passe</button>
            <button class="btn-security" onclick="window.setup2FA()">📱 Activer 2FA</button>
            <button class="btn-security" onclick="window.disable2FA()">🚫 Desactiver 2FA</button>
        </div>
    </div>
</div>

<div id="help-page" class="page">
    <div class="help-section">
        <h2>Aide et documentation</h2>
        <p>Bienvenue sur SENTRAX, votre suite de cybersecurite professionnelle.</p>
        <h3>Comment utiliser SENTRAX ?</h3>
        <ul><li>Entrez une IP ou un domaine</li><li>Choisissez le scanner adapte</li><li>Cliquez sur "Lancer le scan"</li></ul>
        <h3>Les 10 scanners disponibles</h3>
        <ul>{% for s in scanners %}<li><strong>{{ s.name }}</strong> - {{ s.desc }}</li>{% endfor %}</ul>
        <h3>Securite</h3>
        <ul><li>Authentification JWT</li><li>Double authentification (2FA)</li><li>Rate limiting anti-bruteforce</li><li>Reinitialisation mot de passe</li></ul>
        <h3>Support</h3>
        <p>Email: patrickndaye919@gmail.com</p>
        <p>Version: {{ version }}</p>
    </div>
</div>

<div class="footer">SENTRAX {{ version }} | Suite de cybersecurite professionnelle | 10 scanners integres</div>
</div>
</body>
</html>
"""

# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def index():
    return redirect("/login")


@app.route("/login")
def login_page():
    return Response(LOGIN_HTML, mimetype="text/html")


@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_HTML, scanners=SCANNERS, version=API_VERSION)


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password:
        return jsonify({"error": "Username et password requis"}), 400
    
    valid, msg = validate_password_strength(password)
    if not valid:
        return jsonify({"error": f"Mot de passe invalide: {msg}"}), 400
    
    if create_user(username, password, email):
        log_security_event("user_registered", username, request.remote_addr, "Nouvel utilisateur")
        return jsonify({"message": "Compte cree"})
    return jsonify({"error": "Utilisateur existe deja"}), 409


@app.route("/api/login", methods=["POST"])
@rate_limit
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    twofa_code = data.get("twofa_code")
    user = get_user(username)
    if not user:
        log_security_event("login_failed", username, request.remote_addr, "Utilisateur inconnu")
        return jsonify({"error": "Identifiants invalides"}), 401
    if not check_password_hash(user["password"], password):
        log_security_event("login_failed", username, request.remote_addr, "Mauvais mot de passe")
        return jsonify({"error": "Identifiants invalides"}), 401
    if user.get("twofa_enabled"):
        if not twofa_code:
            return jsonify({"need_2fa": True}), 401
        totp = pyotp.TOTP(user["twofa_secret"])
        if not totp.verify(twofa_code):
            log_security_event("login_failed", username, request.remote_addr, "Code 2FA invalide")
            return jsonify({"error": "Code 2FA invalide"}), 401
    token = generate_token(username)
    log_security_event("login_success", username, request.remote_addr, "Connexion reussie")
    return jsonify({"token": token, "username": username})


@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    """Génère un lien de réinitialisation fiable"""
    data = request.get_json()
    username = data.get("username")
    
    user = get_user(username)
    if not user:
        return jsonify({"error": "Utilisateur inconnu"}), 404
    
    token = secrets.token_urlsafe(48)
    expires = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    save_reset_token(token, username, expires)
    
    # ⚠️ DOMAINE FIXE - PAS depuis request.host
    DOMAIN = os.getenv("DOMAIN", "http://localhost:5000")
    reset_link = f"{DOMAIN}/reset/{token}"
    
    log_security_event("reset_request", username, request.remote_addr, "Lien genere")
    
    return jsonify({
        "success": True,
        "link": reset_link,
        "expires_in": "1 heure",
        "brand": "SENTRAX"
    })

@app.route("/reset/<token>")
def reset_form(token):
    data = get_reset_token(token)
    if not data:
        return "<html><body><h1>Lien invalide ou expire</h1><a href='/login'>Retour</a></body></html>", 400
    
    return """
<!DOCTYPE html>
<html>
<head><title>SENTRAX - Reinitialisation</title>
<style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:#0a0a0a;font-family:'Segoe UI',monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;}
    .container{background:#1a1a1a;padding:40px;border-radius:10px;border:1px solid #00ff88;width:400px;text-align:center;}
    .logo{font-size:48px;margin-bottom:20px;}
    h1{color:#00ff88;margin-bottom:20px;}
    .password-container{position:relative;width:100%;margin:10px 0;}
    .password-container input{width:100%;padding:12px;padding-right:45px;background:#0a0a0a;border:1px solid #00ff88;color:#00ff88;border-radius:5px;box-sizing:border-box;}
    .password-toggle{position:absolute;right:12px;top:50%;transform:translateY(-50%);cursor:pointer;font-size:1.2em;}
    button{width:100%;padding:12px;background:#00ff88;color:#000;border:none;border-radius:5px;cursor:pointer;font-weight:bold;}
    .error{color:#ff4444;margin-top:10px;display:none;padding:10px;background:#330000;border-radius:5px;}
    .success{color:#00ff88;margin-top:10px;display:none;padding:10px;background:#003300;border-radius:5px;}
</style>
</head>
<body>
<div class="container">
    <div class="logo">🛡️ SENTRAX</div>
    <h1>Nouveau mot de passe</h1>
    <div class="password-container">
        <input type="password" id="password" placeholder="Nouveau mot de passe">
        <span class="password-toggle" onclick="togglePassword('password', this)">👁️</span>
    </div>
    <div class="password-container">
        <input type="password" id="confirm" placeholder="Confirmer">
        <span class="password-toggle" onclick="togglePassword('confirm', this)">👁️</span>
    </div>
    <button onclick="reset()">Changer</button>
    <div id="error" class="error"></div>
    <div id="success" class="success"></div>
</div>
<script>
    var resetToken = '""" + token + """';
    
    window.togglePassword = function(id, btn){
        var x = document.getElementById(id);
        if(x.type === "password"){
            x.type = "text";
            btn.textContent = "🙈";
        }else{
            x.type = "password";
            btn.textContent = "👁️";
        }
    };
    
    window.showMessage = function(message, isError){
        var errorDiv = document.getElementById('error');
        var successDiv = document.getElementById('success');
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
        
        if(isError){
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }else{
            successDiv.textContent = message;
            successDiv.style.display = 'block';
        }
    };
    
    async function reset() {
        var pwd = document.getElementById('password').value;
        var confirm = document.getElementById('confirm').value;
        
        if(pwd !== confirm) {
            showMessage('Les mots de passe ne correspondent pas', true);
            return;
        }
        if(pwd.length < 8) {
            showMessage('Mot de passe trop court (minimum 8 caracteres)', true);
            return;
        }
        if(!/[A-Z]/.test(pwd)) {
            showMessage('Ajoutez au moins une majuscule', true);
            return;
        }
        if(!/[a-z]/.test(pwd)) {
            showMessage('Ajoutez au moins une minuscule', true);
            return;
        }
        if(!/[0-9]/.test(pwd)) {
            showMessage('Ajoutez au moins un chiffre', true);
            return;
        }
        if(!/[!@#$%^&*()]/.test(pwd)) {
            showMessage('Ajoutez un caractere special (!@#$%^&*())', true);
            return;
        }
        
        try {
            var response = await fetch('/api/reset-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({token: resetToken, new_password: pwd})
            });
            
            var data = await response.json();
            
            if (response.ok) {
                showMessage('✅ Mot de passe modifie avec succes ! Redirection...', false);
                setTimeout(function() {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showMessage('❌ ' + (data.error || 'Erreur lors de la reinitialisation'), true);
            }
        } catch(err) {
            showMessage('❌ Erreur de connexion: ' + err.message, true);
        }
    }
</script>
</body>
</html>
"""

@app.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")
    reset_data = get_reset_token(token)
    if not reset_data:
        return jsonify({"error": "Lien invalide ou expire"}), 400
    
    valid, msg = validate_password_strength(new_password)
    if not valid:
        return jsonify({"error": f"Mot de passe invalide: {msg}"}), 400
    
    username = reset_data["username"]
    update_password(username, new_password)
    mark_token_used(token)
    log_security_event("password_reset", username, request.remote_addr, "Reinitialisation reussie")
    return jsonify({"message": "Mot de passe reinitialise"})


@app.route("/api/logout", methods=["POST"])
@token_required
def logout():
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token[7:]
    tokens_blacklist.add(token)
    return jsonify({"message": "Deconnecte"})


@app.route("/api/change-password", methods=["POST"])
@token_required
def change_password():

    data = request.get_json(silent=True) or {}

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    # 🔴 Validation input stricte
    if not old_password or not new_password:
        return jsonify({
            "error": "Missing fields",
            "code": "MISSING_FIELDS"
        }), 400

    # 🔴 Sécurité: user obligatoire
    if not hasattr(request, "user") or not request.user:
        return jsonify({
            "error": "Unauthorized",
            "code": "NO_USER_CONTEXT"
        }), 401

    username = request.user.get("username")
    if not username:
        return jsonify({
            "error": "Invalid token context",
            "code": "INVALID_TOKEN_CONTEXT"
        }), 401

    user = get_user(username)

    if not user:
        return jsonify({
            "error": "User not found",
            "code": "USER_NOT_FOUND"
        }), 404

    # 🔴 Vérification ancien mot de passe
    if not check_password_hash(user.get("password", ""), old_password):
        return jsonify({
            "error": "Ancien mot de passe incorrect",
            "code": "INVALID_OLD_PASSWORD"
        }), 403

    # 🔴 Validation nouveau mot de passe
    valid, msg = validate_password_strength(new_password)
    if not valid:
        return jsonify({
            "error": msg,
            "code": "WEAK_PASSWORD"
        }), 400

    try:
        update_password(username, new_password)

        log_security_event(
            "password_changed",
            username,
            request.remote_addr,
            "Mot de passe modifié"
        )

        return jsonify({
            "message": "Mot de passe changé avec succès",
            "code": "PASSWORD_CHANGED"
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "code": "UPDATE_FAILED"
        }), 500
@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "version": API_VERSION, "time": datetime.now().isoformat()})


@app.route("/api/verify")
@token_required
def verify():
    return jsonify({"valid": True, "username": request.user["username"]})


@app.route("/api/scanners")
@token_required
def get_scanners():
    return jsonify(SCANNERS)


@app.route("/api/2fa/setup", methods=["POST"])
@token_required
def setup_2fa():
    username = request.user["username"]
    user = get_user(username)
    if user.get("twofa_enabled"):
        return jsonify({"error": "2FA deja activee"}), 400
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(username, issuer_name="SENTRAX")
    qr = qrcode.make(uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({"secret": secret, "qr_code": f"data:image/png;base64,{qr_base64}"})


@app.route("/api/2fa/verify", methods=["POST"])
@token_required
def verify_2fa():
    data = request.get_json()
    secret = data.get("secret")
    code = data.get("code")
    totp = pyotp.TOTP(secret)
    if not totp.verify(code):
        return jsonify({"error": "Code invalide"}), 401
    enable_2fa(request.user["username"], secret)
    return jsonify({"message": "2FA activee"})


@app.route("/api/2fa/disable", methods=["POST"])
@token_required
def disable_2fa():
    data = request.get_json()
    code = data.get("code")
    user = get_user(request.user["username"])
    if not user.get("twofa_secret"):
        return jsonify({"error": "2FA non activee"}), 400
    totp = pyotp.TOTP(user["twofa_secret"])
    if not totp.verify(code):
        return jsonify({"error": "Code invalide"}), 401
    disable_2fa_user(request.user["username"])
    return jsonify({"message": "2FA desactivee"})


@app.route("/api/scan", methods=["POST"])
@token_required
def start_scan():
    data = request.get_json()
    target = data.get("target")
    scanner = data.get("scanner", "expert")
    if not validate_target(target):
        return jsonify({"error": "Cible invalide"}), 400
    scan_id = str(uuid.uuid4())[:8]
    scans[scan_id] = {"id": scan_id, "target": target, "scanner": scanner, "status": "running", "started_at": datetime.now().isoformat()}

    def run_scan():
        try:
            ip = socket.gethostbyname(target)
            open_ports = []
            ports = [21, 22, 25, 53, 80, 110, 443, 3306, 8080, 8443]
            for port in ports:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    if s.connect_ex((ip, port)) == 0:
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "unknown"
                        open_ports.append({"port": port, "service": service})
                    s.close()
                except:
                    pass
            scans[scan_id]["status"] = "completed"
            scans[scan_id]["results"] = {"target": target, "ip": ip, "scanner": scanner, "open_ports": open_ports, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            scans[scan_id]["status"] = "failed"
            scans[scan_id]["error"] = str(e)
    threading.Thread(target=run_scan).start()
    return jsonify({"scan_id": scan_id, "status": "started"})


@app.route("/api/scan/<scan_id>")
@token_required
def get_scan(scan_id):
    if scan_id not in scans:
        return jsonify({"error": "Not found"}), 404
    return jsonify(scans[scan_id])


@app.route("/api/export/pdf/<scan_id>")
@token_required
def export_pdf(scan_id):
    if scan_id not in scans:
        return "Scan not found", 404
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 800, "SENTRAX - Rapport de scan")
    scan = scans[scan_id]
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"Scan ID: {scan_id}")
    pdf.drawString(50, 740, f"Cible: {scan['target']}")
    pdf.drawString(50, 720, f"Scanner: {scan['scanner']}")
    pdf.drawString(50, 700, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = 660
    results = scan.get("results", {})
    ports = results.get("open_ports", [])
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Ports ouverts:")
    y -= 30
    pdf.setFont("Helvetica", 10)
    for p in ports:
        pdf.drawString(50, y, f"Port {p['port']} : {p['service']}")
        y -= 20
        if y < 50:
            pdf.showPage()
            y = 800
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", download_name=f"sentrax_scan_{scan_id}.pdf")


def cleanup_reset_tokens():
    while True:
        time.sleep(3600)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reset_tokens WHERE expires_at < strftime('%Y-%m-%d %H:%M:%S', 'now')")
            conn.commit()
            conn.close()
        except:
            pass

def setup_flask_port():
    ports = [5000, 5001, 5002, 8080, 8081]
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 5000

def banner(port):
    print("=" * 60)
    print("🛡️  SENTRAX API v3.1.0")
    print("=" * 60)
    print(f"🌐 Dashboard : http://localhost:{port}/dashboard")
    print(f"🔐 Login     : http://localhost:{port}/login")
    print(f"🔌 Port      : {port}")
    print(f"📡 Scanners disponibles: 10")
    if EMAIL_CONFIGURED:
        print("📧 Email      : Configure")
    else:
        print("📧 Email      : Non configure (les liens seront affiches dans la console)")
    print("=" * 60)


if __name__ == "__main__":
    cleanup_thread = threading.Thread(target=cleanup_reset_tokens, daemon=True)
    cleanup_thread.start()
    port = setup_flask_port()
    banner(port)
    try:
        app.run(host="127.0.0.1", port=port, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 SENTRAX arrete proprement")
    except Exception as e:
        print(f"\n[ERREUR FATALE] {e}")