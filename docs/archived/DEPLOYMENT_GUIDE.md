#  KAILASH-AEGISHU Deployment Guide

## System Overview

**Application:** AEGIS HU with integrated KAILASH AI System  
**Stack:** React (rontend) + astAPI (ackend) + MongoD  
**Domain:** rudraaa.in (target deployment)  
**Current:** https://ganesha-v2-api.preview.emergentagent.com (preview)

---

##  Server Requirements

### Minimum Specifications:
- **Operating System:** Ubuntu .4 LTS or later
- **RAM:** 4G minimum, 8G recommended
- **CPU:**  cores minimum, 4 cores recommended
- **Storage:** G minimum, G recommended
- **andwidth:**  Mbps minimum

### Software Requirements:
- Python 3.+
- Node.js 8+ and Yarn
- MongoD .+
- Nginx
- Supervisor (process management)
- Certbot (for SSL certificates)

---

##  Installation Steps

### . Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3. python3.-venv python3-pip \
    nodejs npm mongodb nginx supervisor certbot \
    python3-certbot-nginx git curl build-essential

# Install Yarn
npm install -g yarn

# Create application directory
sudo mkdir -p /opt/aegishub
sudo chown $USER:$USER /opt/aegishub
cd /opt/aegishub
```

### . Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/G4GURGAA/AEGISHU.git .

# Or pull latest
git pull origin main
```

### 3. ackend Setup

```bash
cd /opt/aegishub/backend

# Create virtual environment
python3. -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production .env file
cat > .env << 'EO'
# MongoD Configuration
MONGO_URL="mongodb://localhost:"
D_NAME="kailash"

# CORS Configuration
CORS_ORIGINS="https://rudraaa.in"

# JWT Configuration
JWT_SECRET="CHANGE-THIS-TO-SECURE-RANDOM-STRING-IN-PRODUCTION"
JWT_ALGORITHM="HS"

# CEO Authentication
CEO_KEY="CHANGE-THIS-IN-PRODUCTION"

# Anthropic AI Configuration (Optional)
ANTHROPIC_API_KEY=""

# ackend URL
API_ASE_URL="https://rudraaa.in"
EO

# Generate secure secrets
echo "JWT_SECRET=$(openssl rand -hex 3)" >> .env
echo "CEO_KEY=$(openssl rand -hex )" >> .env

echo "[WARN]  IMPORTANT: Save these secrets securely!"
cat .env | grep -E "JWT_SECRET|CEO_KEY"
```

### 4. rontend Setup

```bash
cd /opt/aegishub/frontend

# Install dependencies
yarn install

# Create production .env file
cat > .env << 'EO'
REACT_APP_ACKEND_URL=https://rudraaa.in
WDS_SOCKET_PORT=443
REACT_APP_ENALE_VISUAL_EDITS=false
ENALE_HEALTH_CHECK=false
EO

# uild production bundle
yarn build
```

### . MongoD Setup

```bash
# Start MongoD
sudo systemctl start mongod
sudo systemctl enable mongod

# Create admin user (optional but recommended)
mongosh << 'EO'
use admin
db.createUser({
  user: "aegisadmin",
  pwd: "CHANGE-THIS-PASSWORD",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
})
EO

# Create application database
mongosh << 'EO'
use kailash
db.createCollection("status_checks")
db.createCollection("tasks")
db.createCollection("commands")
db.createCollection("departments")
db.createCollection("agent_activity")
EO
```

### . Nginx Configuration

```bash
# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/aegishub << 'EO'
# AEGISHU Nginx Configuration

# Redirect HTTP to HTTPS
server {
    listen 8;
    listen [::]:8;
    server_name rudraaa.in www.rudraaa.in;
    
    return 3 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http;
    listen [::]:443 ssl http;
    server_name rudraaa.in www.rudraaa.in;

    # SSL Configuration (Certbot will add these)
    # ssl_certificate /etc/letsencrypt/live/rudraaa.in/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/rudraaa.in/privkey.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf;
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security Headers
    add_header X-rame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "; mode=block" always;
    add_header Strict-Transport-Security "max-age=33; includeSubDomains" always;

    # rontend (React)
    location / {
        proxy_pass http://localhost:3;
        proxy_http_version .;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-orwarded-or $proxy_add_x_forwarded_for;
        proxy_set_header X-orwarded-Proto $scheme;
    }

    # ackend API (astAPI)
    location /api/ {
        proxy_pass http://localhost:8;
        proxy_http_version .;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-orwarded-or $proxy_add_x_forwarded_for;
        proxy_set_header X-orwarded-Proto $scheme;
        
        # Increase timeouts for AI processing
        proxy_read_timeout 3s;
        proxy_connect_timeout s;
    }

    # WebSocket Support
    location /ws/ {
        proxy_pass http://localhost:8;
        proxy_http_version .;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 84;
    }

    # Static files (production)
    location /static/ {
        alias /opt/aegishub/frontend/build/static/;
        expires y;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/aegishub_access.log;
    error_log /var/log/nginx/aegishub_error.log;
}
EO

# Enable site
sudo ln -s /etc/nginx/sites-available/aegishub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### . SSL Certificate Setup

```bash
# Install SSL certificate using Certbot
sudo certbot --nginx -d rudraaa.in -d www.rudraaa.in

# Test automatic renewal
sudo certbot renew --dry-run
```

### 8. Supervisor Configuration

```bash
# ackend service
sudo cat > /etc/supervisor/conf.d/aegishub-backend.conf << 'EO'
[program:aegishub-backend]
directory=/opt/aegishub/backend
command=/opt/aegishub/backend/venv/bin/uvicorn server:app --host ... --port 8 --workers 4
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/supervisor/aegishub-backend.err.log
stdout_logfile=/var/log/supervisor/aegishub-backend.out.log
environment=PATH="/opt/aegishub/backend/venv/bin"
EO

# rontend service
sudo cat > /etc/supervisor/conf.d/aegishub-frontend.conf << 'EO'
[program:aegishub-frontend]
directory=/opt/aegishub/frontend
command=/usr/bin/yarn start
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/supervisor/aegishub-frontend.err.log
stdout_logfile=/var/log/supervisor/aegishub-frontend.out.log
environment=PORT="3",NODE_ENV="production"
EO

# MongoD service (if not using system service)
# Already managed by systemd

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 9. Verify Deployment

```bash
# Check services status
sudo supervisorctl status all
sudo systemctl status nginx
sudo systemctl status mongod

# Check backend health
curl http://localhost:8/api/
curl http://localhost:8/api/kailash/health

# Check frontend
curl http://localhost:3

# Check via domain (after DNS is configured)
curl https://rudraaa.in/api/
```

---

##  Security Configuration

### . irewall Setup

```bash
# Install UW
sudo apt install ufw

# Allow SSH, HTTP, HTTPS
sudo ufw allow /tcp
sudo ufw allow 8/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### . MongoD Security

```bash
# Edit MongoD config
sudo nano /etc/mongod.conf

# Add authentication
security:
  authorization: enabled

# Restart MongoD
sudo systemctl restart mongod
```

### 3. Application Security

- Change all default passwords in `.env` files
- Use strong JWT secrets (3+ characters)
- Enable HTTPS only (disable HTTP)
- Configure CORS properly (allow only your domain)
- Regular security updates: `sudo apt update && sudo apt upgrade`

---

##  Monitoring & Maintenance

### . Log Management

```bash
# View backend logs
sudo tail -f /var/log/supervisor/aegishub-backend.out.log
sudo tail -f /var/log/supervisor/aegishub-backend.err.log

# View frontend logs
sudo tail -f /var/log/supervisor/aegishub-frontend.out.log

# View Nginx logs
sudo tail -f /var/log/nginx/aegishub_access.log
sudo tail -f /var/log/nginx/aegishub_error.log

# View MongoD logs
sudo journalctl -u mongod -f
```

### . Log Rotation

```bash
# Create logrotate config
sudo cat > /etc/logrotate.d/aegishub << 'EO'
/var/log/supervisor/aegishub-*.log {
    daily
    rotate 4
    compress
    delaycompress
    notifempty
    missingok
    postrotate
        supervisorctl restart aegishub-backend aegishub-frontend
    endscript
}
EO
```

### 3. ackup Strategy

```bash
# Create backup script
cat > /opt/aegishub/backup.sh << 'EO'
#!/bin/bash
# AEGISHU ackup Script

ACKUP_DIR="/opt/aegishub/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $ACKUP_DIR

# ackup MongoD
mongodump --db kailash --out $ACKUP_DIR/mongo_$DATE

# ackup application files
tar -czf $ACKUP_DIR/app_$DATE.tar.gz /opt/aegishub \
    --exclude=/opt/aegishub/backups \
    --exclude=/opt/aegishub/node_modules \
    --exclude=/opt/aegishub/backend/venv

# Keep only last  days of backups
find $ACKUP_DIR -type f -mtime + -delete

echo "ackup completed: $DATE"
EO

chmod +x /opt/aegishub/backup.sh

# Add to crontab (daily at  AM)
(crontab -l >/dev/null; echo "  * * * /opt/aegishub/backup.sh") | crontab -
```

### 4. Health Check Monitoring

```bash
# Create health check script
cat > /opt/aegishub/health_check.sh << 'EO'
#!/bin/bash
# AEGISHU Health Check Script

ACKEND_URL="http://localhost:8/api/"
RONTEND_URL="http://localhost:3"
MONGO_URL="mongodb://localhost:"

# Check backend
if curl -s -o /dev/null -w "%{http_code}" $ACKEND_URL | grep -q ""; then
    echo "[OK] ackend: HEALTHY"
else
    echo "[AIL] ackend: UNHEALTHY"
    sudo supervisorctl restart aegishub-backend
fi

# Check frontend
if curl -s -o /dev/null -w "%{http_code}" $RONTEND_URL | grep -q ""; then
    echo "[OK] rontend: HEALTHY"
else
    echo "[AIL] rontend: UNHEALTHY"
    sudo supervisorctl restart aegishub-frontend
fi

# Check MongoD
if mongosh --eval "db.adminCommand('ping')" > /dev/null >&; then
    echo "[OK] MongoD: HEALTHY"
else
    echo "[AIL] MongoD: UNHEALTHY"
    sudo systemctl restart mongod
fi
EO

chmod +x /opt/aegishub/health_check.sh

# Add to crontab (every  minutes)
(crontab -l >/dev/null; echo "*/ * * * * /opt/aegishub/health_check.sh >> /var/log/aegishub_health.log >&") | crontab -
```

---

##  Deployment Updates

### Update Procedure

```bash
# Create update script
cat > /opt/aegishub/update.sh << 'EO'
#!/bin/bash
# AEGISHU Update Script

cd /opt/aegishub

# ackup first
./backup.sh

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Update frontend
cd frontend
yarn install
yarn build
cd ..

# Restart services
sudo supervisorctl restart all

echo "[OK] Update completed successfully"
EO

chmod +x /opt/aegishub/update.sh
```

### Rollback Procedure

```bash
# If update fails, rollback to previous version
cd /opt/aegishub
git log --oneline -n   # ind previous commit
git reset --hard <commit-hash>
./update.sh
```

---

##  DNS Configuration

### or rudraaa.in domain:

. **A Record:**
   - Host: `@`
   - Value: `YOUR_SERVER_IP`
   - TTL: `3`

. **A Record (www):**
   - Host: `www`
   - Value: `YOUR_SERVER_IP`
   - TTL: `3`

3. **CNAME Record (optional subdomains):**
   - Host: `api`
   - Value: `rudraaa.in`
   - TTL: `3`

### Verify DNS:

```bash
dig rudraaa.in
dig www.rudraaa.in
nslookup rudraaa.in
```

---

##  Post-Deployment Checklist

- [ ] All services running (`supervisorctl status all`)
- [ ] ackend API responding (`curl https://rudraaa.in/api/`)
- [ ] rontend accessible (`curl https://rudraaa.in/`)
- [ ] KAILASH health check passing (`curl https://rudraaa.in/api/kailash/health`)
- [ ] SSL certificate active (`curl -I https://rudraaa.in/`)
- [ ] Login flow working (test with browser)
- [ ] KAILASH integration working (test GANESHA chat)
- [ ] MongoD accessible and secured
- [ ] irewall configured (`sudo ufw status`)
- [ ] ackups scheduled (`crontab -l`)
- [ ] Health checks running (`tail /var/log/aegishub_health.log`)
- [ ] Logs rotating properly
- [ ] DNS propagated (`dig rudraaa.in`)

---

## 🆘 Troubleshooting

### ackend not starting:

```bash
# Check logs
sudo tail - /var/log/supervisor/aegishub-backend.err.log

# Common issues:
# - Missing dependencies: pip install -r requirements.txt
# - Port conflict: Check if 8 is already in use
# - MongoD not running: sudo systemctl start mongod
# - Environment variables: Check .env file
```

### rontend not starting:

```bash
# Check logs
sudo tail - /var/log/supervisor/aegishub-frontend.err.log

# Common issues:
# - Node modules missing: yarn install
# - Port conflict: Check if 3 is already in use
# - uild errors: yarn build
```

### MongoD connection failed:

```bash
# Check MongoD status
sudo systemctl status mongod

# Check logs
sudo journalctl -u mongod -n 

# Restart MongoD
sudo systemctl restart mongod
```

### SSL certificate issues:

```bash
# Renew certificate
sudo certbot renew

# orce renewal
sudo certbot renew --force-renewal

# Check certificate status
sudo certbot certificates
```

---

##  Support

or issues or questions:
- GitHub: https://github.com/G4GURGAA/AEGISHU
- Documentation: This file
- Health Check: https://rudraaa.in/api/health

---

##  Notes

- Always backup before making changes
- Test updates in staging environment first
- Monitor logs after deployment
- Keep secrets secure and never commit to Git
- Regular security updates are critical
- Document any custom configurations

---

**Deployment Guide Version:** .  
**Last Updated:** --  
**Target Domain:** rudraaa.in  
**Status:** Ready for Production Deployment
