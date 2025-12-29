# Rabah ERP - Web Version

Web-based version of the Rabah ERP inventory management system, designed to run on GitHub Pages.

## Features

- ✅ **Authentication System** - Login page with admin username/password
- ✅ **Product Management** - Add, edit, delete products (Fans, Sheet Metal, Flexible)
- ✅ **Search & Sort** - Real-time search and sorting capabilities
- ✅ **Data Persistence** - Uses browser localStorage (data saved locally)
- ✅ **Responsive Design** - Works on desktop and mobile devices
- ✅ **RTL Support** - Right-to-left layout for Arabic interface

## Default Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change the password after first login for security!

## Changing Admin Password

You can change the admin password by opening the browser console (F12) and running:

```javascript
authManager.changePassword('your_new_password');
```

Or modify the password directly in `auth.js` before deploying.

## Deployment to GitHub Pages

### Step 1: Create GitHub Repository

1. Create a new repository on GitHub
2. Name it (e.g., `rabah-erp-web`)

### Step 2: Upload Files

1. Upload all files from the `web/` folder to your repository
2. Files should be in the root of the repository (or in a folder)

### Step 3: Enable GitHub Pages

1. Go to your repository settings
2. Scroll to "Pages" section
3. Under "Source", select the branch (usually `main` or `master`)
4. Select the folder (root or `/docs` if you put files in docs folder)
5. Click "Save"

### Step 4: Access Your Application

Your application will be available at:
```
https://yourusername.github.io/repository-name/
```

## File Structure

```
web/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── auth.js             # Authentication logic
├── database.js          # Database operations (localStorage)
├── app.js              # Main application logic
└── README.md           # This file
```

## Data Storage

The application uses browser `localStorage` to store:
- User authentication (admin credentials)
- All product data (fans, sheet metal, flexible)
- User session

⚠️ **Note:** Data is stored locally in the browser. If you clear browser data, all information will be lost. Consider implementing data export/import features for backup.

## Limitations

Since this runs on GitHub Pages (static hosting):

1. **No Backend Server** - All processing happens in the browser
2. **Local Storage Only** - Data is stored in the user's browser
3. **No File Uploads** - Cannot upload catalog files directly (can use URLs)
4. **Word Export** - Would need a JavaScript library like `docx.js` for Word document generation

## Future Enhancements

- [ ] Word document export using `docx.js`
- [ ] Data export/import (JSON backup)
- [ ] Multiple user support
- [ ] Cloud storage integration
- [ ] File upload for catalog PDFs

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

Requires modern browser with localStorage support (all major browsers).

## Security Notes

⚠️ **Important Security Considerations:**

1. **Client-Side Only** - All code is visible to users
2. **Simple Password Hash** - Current implementation uses basic hashing
3. **No HTTPS Required** - But recommended for production
4. **Local Storage** - Can be cleared by users

For production use, consider:
- Implementing proper password hashing (bcrypt, etc.)
- Using a backend server for authentication
- Implementing proper session management
- Using HTTPS

## Troubleshooting

### Application doesn't load
- Check browser console for errors (F12)
- Ensure all JavaScript files are loaded
- Check GitHub Pages deployment status

### Can't login
- Default credentials: `admin` / `admin123`
- Clear browser localStorage and refresh
- Check browser console for errors

### Data lost
- Data is stored in browser localStorage
- Clearing browser data will delete all information
- Consider implementing export feature for backups

## Support

For issues or questions, check the main project README or create an issue in the repository.

---

**Note:** This is a client-side web application. For a full-featured version with backend support, consider deploying the Python version on a platform like Heroku, Render, or PythonAnywhere.

