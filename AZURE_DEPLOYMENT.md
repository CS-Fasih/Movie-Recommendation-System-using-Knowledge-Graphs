# Azure Deployment Guide

## 🚀 Deploying to Azure Web Apps

This guide will help you deploy the Movie Recommendation System to Azure App Service.

### Prerequisites

1. Azure account (free tier available)
2. Neo4j Aura instance (free tier available)
3. Azure CLI installed (optional, for command-line deployment)

---

## Step 1: Set Up Neo4j Aura (Cloud Database)

1. Go to https://neo4j.com/cloud/aura/
2. Create a free account
3. Create a new database instance
4. **Save your credentials immediately:**
   - Connection URI (e.g., `neo4j+s://xxxxx.databases.neo4j.io`)
   - Username (usually `neo4j`)
   - Password (auto-generated - save it!)

---

## Step 2: Create Azure Web App

### Option A: Azure Portal (GUI)

1. Go to Azure Portal (https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Web App" and click "Create"
4. Configure:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Name**: Choose a unique name (e.g., `movie-rec-system-123`)
   - **Publish**: Code
   - **Runtime stack**: Python 3.10 or 3.11
   - **Operating System**: Linux
   - **Region**: Choose closest to you
   - **Pricing**: Free F1 or Basic B1
5. Click "Review + Create" then "Create"

### Option B: Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name movie-rec-rg --location eastus

# Create app service plan
az appservice plan create --name movie-rec-plan --resource-group movie-rec-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group movie-rec-rg --plan movie-rec-plan --name movie-rec-system-123 --runtime "PYTHON:3.10"
```

---

## Step 3: Configure Environment Variables

### In Azure Portal:

1. Go to your Web App
2. Navigate to **Configuration** → **Application settings**
3. Add the following settings (click "New application setting" for each):

| Name | Value | Example |
|------|-------|---------|
| `NEO4J_URI` | Your Neo4j Aura URI | `neo4j+s://xxxxx.databases.neo4j.io` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Your Neo4j password | `your-password-here` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | `true` |
| `PORT` | (Auto-set by Azure) | Leave empty |

4. Click **Save** at the top

### Using Azure CLI:

```bash
az webapp config appsettings set --resource-group movie-rec-rg --name movie-rec-system-123 --settings \
  NEO4J_URI="neo4j+s://xxxxx.databases.neo4j.io" \
  NEO4J_USERNAME="neo4j" \
  NEO4J_PASSWORD="your-password-here" \
  SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

---

## Step 4: Configure Startup Command

1. In Azure Portal, go to your Web App
2. Navigate to **Configuration** → **General settings**
3. Set **Startup Command** to:
   ```bash
   bash startup.sh
   ```
4. Click **Save**

### Using Azure CLI:

```bash
az webapp config set --resource-group movie-rec-rg --name movie-rec-system-123 --startup-file "bash startup.sh"
```

---

## Step 5: Deploy Your Code

### Option A: GitHub Actions (Recommended)

1. In Azure Portal, go to your Web App
2. Navigate to **Deployment Center**
3. Select **GitHub** as source
4. Authorize Azure to access your GitHub
5. Select your repository and branch
6. Azure will automatically create a GitHub Actions workflow
7. Click **Save**

Future pushes to your repository will automatically deploy!

### Option B: Local Git Deployment

```bash
# In your project directory
git remote add azure <your-azure-git-url>
git push azure main
```

### Option C: Azure CLI Deployment

```bash
# In your project directory
az webapp up --name movie-rec-system-123 --resource-group movie-rec-rg --runtime "PYTHON:3.10"
```

### Option D: VS Code Azure Extension

1. Install "Azure App Service" extension in VS Code
2. Sign in to Azure
3. Right-click your project folder
4. Select "Deploy to Web App"
5. Choose your web app

---

## Step 6: Seed the Database

After deployment, you need to populate the Neo4j database:

### Option A: Using SSH Console (Recommended for Azure)

1. In Azure Portal, go to your Web App
2. Navigate to **SSH** under Development Tools
3. Run health check first:
   ```bash
   cd /home/site/wwwroot
   python health_check.py
   ```
4. If health check passes, seed the database:
   ```bash
   python data_seeder.py
   ```

### Option B: Using Kudu Console

1. Go to `https://<your-app-name>.scm.azurewebsites.net`
2. Navigate to **Debug console** → **CMD**
3. Navigate to `site/wwwroot`
4. Run:
   ```bash
   python health_check.py
   python data_seeder.py
   ```

### Option C: Locally (if you have Neo4j Aura credentials)

```bash
# Create .env file with your Neo4j Aura credentials
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Run health check
python health_check.py

# Run seeder locally
python data_seeder.py
```

---

## Step 7: Access Your Application

Your app will be available at:
- **URL**: `https://<your-app-name>.azurewebsites.net`
- Example: `https://movie-rec-system-123.azurewebsites.net`

---

## 🔧 Troubleshooting

### Quick Diagnosis

Run the health check script to identify issues:
```bash
python health_check.py
```

This will check:
- Python version compatibility
- Environment variables configuration
- Required dependencies installation
- Neo4j database connection
- Streamlit configuration
- Startup script status

### Issue: "Content is not showing" or Blank Page

**Possible Causes:**

1. **Environment variables not set**
   - Solution: Verify all environment variables in Configuration → Application settings
   - Check that NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD are correct
   - Run: `python health_check.py` to verify

2. **Startup command not configured**
   - Solution: Set startup command to `bash startup.sh` in Configuration → General settings

3. **Database not seeded**
   - Solution: Run `python data_seeder.py` via SSH console
   - First verify connection with `python health_check.py`

4. **Neo4j connection blocked**
   - Solution: Check Neo4j Aura firewall settings, allow Azure IP ranges
   - Test with: `python health_check.py`

5. **Build failed during deployment**
   - Solution: Check deployment logs in Deployment Center
   - Ensure `requirements.txt` is in root directory

### Issue: Application Timeout or Slow Response

**Solutions:**
- Upgrade to Basic or Standard App Service Plan (F1 is very limited)
- Check Neo4j Aura connection latency
- Enable Application Insights for monitoring

### Issue: ModuleNotFoundError

**Solutions:**
- Verify `requirements.txt` includes all dependencies
- Check deployment logs for build errors
- Set `SCM_DO_BUILD_DURING_DEPLOYMENT=true` in app settings

### How to Check Logs

#### Azure Portal:
1. Go to your Web App
2. Navigate to **Monitoring** → **Log stream**
3. View real-time logs

#### Download Logs:
```bash
az webapp log download --resource-group movie-rec-rg --name movie-rec-system-123
```

#### View Specific Logs:
- Application logs: `/home/LogFiles/application.log`
- Python logs: `/home/LogFiles/python.log`
- Deployment logs: Deployment Center → Logs

---

## 🎯 Verification Checklist

Before declaring success, verify:

- [ ] Web app is running (check URL in browser)
- [ ] No error messages on home page
- [ ] Can see movie list dropdown
- [ ] Can select a movie and see details
- [ ] Recommendations are showing
- [ ] Graph visualization works
- [ ] Database statistics appear in sidebar

---

## 📊 Performance Tips

1. **Use Neo4j Aura Free Tier wisely:**
   - Free tier has 50k nodes limit
   - Monitor usage in Neo4j console

2. **Optimize Streamlit:**
   - Use `@st.cache_resource` for database connections (already implemented)
   - Consider reducing movie dataset if too large

3. **Azure App Service:**
   - Free F1 tier: Good for testing, limited performance
   - Basic B1 tier: Recommended for demos/presentations
   - Standard S1+: For production use

4. **Enable Application Insights:**
   - Monitor performance and errors
   - Free tier includes 5GB/month

---

## 🔐 Security Best Practices

1. **Never commit secrets to Git:**
   - `.env` is in `.gitignore` ✓
   - Use Azure App Settings for credentials ✓

2. **Use Neo4j Aura's built-in security:**
   - Auto-encrypted connections (neo4j+s://)
   - Password rotation available

3. **Azure Security:**
   - Enable HTTPS only (default on Azure)
   - Consider Azure Key Vault for production

---

## 💡 Common Questions

**Q: How much does this cost?**
- Neo4j Aura Free: $0 (50k nodes limit)
- Azure App Service F1: $0 (limited resources)
- Azure App Service B1: ~$13/month
- Total minimum: $0 (both free tiers)

**Q: Can I use a custom domain?**
- Yes! In Azure Portal: Custom domains → Add custom domain

**Q: How do I update the deployed app?**
- Just push to GitHub (if using GitHub Actions)
- Or re-run deployment command

**Q: How do I add more movies?**
- Edit `data_seeder.py` and add more movie data
- Re-run the seeder via SSH console

**Q: Can I deploy to other platforms?**
- Yes! Works on:
  - Heroku (with Heroku Postgres addon)
  - AWS Elastic Beanstalk
  - Google Cloud Run
  - Any platform supporting Python and Streamlit

---

## 📞 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io/knowledge-base/deploy/deploy-streamlit-on-azure
- **Azure App Service**: https://docs.microsoft.com/azure/app-service/
- **Neo4j Aura**: https://neo4j.com/docs/aura/
- **GitHub Issues**: Report bugs in your repository

---

## 🎓 For Your Presentation

When demonstrating:

1. Show the live Azure URL (impressive!)
2. Explain you're using cloud services (Neo4j Aura + Azure)
3. Demonstrate scalability potential
4. Show the logs/monitoring (professional touch)
5. Mention cost-effectiveness (free tiers!)

Good luck with your deployment! 🚀
