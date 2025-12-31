# Web Version Deployment Guide

This guide explains how to deploy the Rabah ERP web application to GitHub Pages.

## Quick Start

1. **Create GitHub Repository**
   - Go to GitHub and create a new repository
   - Name it (e.g., `rabah-erp-web`)

2. **Upload Files**
   - Upload all files from the `web/` folder to your repository
   - Files should be in the root directory

3. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Select source branch (usually `main`)
   - Select folder (root `/`)
   - Click Save

4. **Access Your App**
   - Your app will be available at: `https://yourusername.github.io/repository-name/`

## Detailed Steps

### Step 1: Prepare Files

All files needed are in the `web/` folder:
- `index.html`
- `styles.css`
- `auth.js`
- `database.js`
- `app.js`
- `README.md`

### Step 2: Create Repository

1. Log in to GitHub
2. Click the "+" icon → "New repository"
3. Name your repository (e.g., `rabah-erp`)
4. Choose public or private
5. **Don't** initialize with README (we already have files)
6. Click "Create repository"

### Step 3: Upload Files

**Option A: Using GitHub Web Interface**
1. Click "uploading an existing file"
2. Drag and drop all files from `web/` folder
3. Commit changes

**Option B: Using Git Command Line**
```bash
cd web
git init
git add .
git commit -m "Initial commit - Web version"
git branch -M main
git remote add origin https://github.com/yourusername/rabah-erp.git
git push -u origin main
```

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" section (left sidebar)
4. Under "Source":
   - Branch: Select `main` (or `master`)
   - Folder: Select `/ (root)`
5. Click "Save"

### Step 5: Wait for Deployment

- GitHub Pages takes 1-2 minutes to deploy
- You'll see a green checkmark when ready
- Your site URL will be shown in the Pages settings

### Step 6: Access Your Application

Visit: `https://yourusername.github.io/repository-name/`

## Custom Domain (Optional)

If you want to use a custom domain:
1. In Pages settings, enter your domain name
2. Add a `CNAME` file in your repository with your domain
3. Configure DNS settings with your domain provider

## Updating the Application

To update your deployed application:

1. Make changes to files locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update application"
   git push
   ```
3. Changes will be live in 1-2 minutes

## Default Login

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Change the password before deploying to production!**

To change password, edit `auth.js`:
```javascript
// Change default password
localStorage.setItem('admin_password', authManager.hashPassword('your_new_password'));
```

## Troubleshooting

### Pages not showing
- Check that `index.html` is in the root directory
- Verify Pages is enabled in Settings
- Wait a few minutes for deployment

### 404 Error
- Ensure you're using the correct URL format
- Check repository name matches URL
- Verify branch name is correct

### Application not working
- Open browser console (F12) to check for errors
- Verify all JavaScript files are loading
- Check that localStorage is enabled in browser

### Can't login
- Default credentials: `admin` / `admin123`
- Clear browser localStorage if needed
- Check browser console for errors

## Security Considerations

⚠️ **Important:**
- This is a client-side application
- All code is visible to users
- Password hashing is basic (not production-grade)
- Data is stored in browser localStorage

For production use, consider:
- Implementing proper backend authentication
- Using a database server
- Implementing HTTPS
- Using proper password hashing (bcrypt, etc.)

## Features Status

✅ **Working:**
- Login/Authentication
- Product management (Add/Edit/Delete)
- Search and sorting
- Data persistence (localStorage)
- Multiple product types

⚠️ **To Be Implemented:**
- Word document export (needs `docx.js` library)
- File upload for catalog PDFs
- Data export/import
- Advanced price list features

## Next Steps

1. Deploy to GitHub Pages
2. Test all features
3. Change default password
4. Share the URL with users
5. Consider implementing Word export feature

---

For questions or issues, refer to the main project documentation.


